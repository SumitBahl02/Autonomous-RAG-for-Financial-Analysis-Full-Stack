import { google } from "googleapis";
import multer from "multer";
import fs from "fs";
import path from "path";
import { NextApiRequest, NextApiResponse } from "next";

// Configure multer for file uploads
const upload = multer({ dest: "/tmp" });

export const config = {
  api: {
    bodyParser: false, // Disable default body parser
  },
};

const handler = async (req: NextApiRequest, res: NextApiResponse) => {
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  const multerPromise = (): Promise<Express.Multer.File> =>
    new Promise((resolve, reject) => {
      upload.single("file")(req as any, {} as any, (err: any) => {
        if (err) reject(err);
        else resolve((req as any).file as Express.Multer.File);
      });
    });

  try {
    const file = await multerPromise();

    // Authenticate using the key.json file
    const auth = new google.auth.GoogleAuth({
      keyFile: path.resolve(process.cwd(), "pathway-441510-85ba5963ffc8.json"),
      scopes: ["https://www.googleapis.com/auth/drive"],
    });

    const drive = google.drive({ version: "v3", auth });

    // Upload file to Google Drive
    const fileMetadata = {
      name: file.originalname,
      parents: ["1GNg1IpKbFzk2Hlj_JTekTckRQ0KtSE19"], // Replace with the folder ID in Google Drive where you want to upload
    };

    const media = {
      mimeType: file.mimetype,
      body: fs.createReadStream(file.path),
    };

    const response = await drive.files.create({
      requestBody: fileMetadata,
      media: media,
      fields: "id",
    });

    // Make the file public
    await drive.permissions.create({
      fileId: (response.data as any).id,
      requestBody: {
        role: "reader",
        type: "anyone",
      },
    });

    // Generate public URL
    const publicUrl = await drive.files.get({
      fileId: response.data.id as string,
      fields: "webViewLink, webContentLink",
    }) as unknown as { data: { webViewLink: string; webContentLink: string } };

    // Clean up the uploaded file from /tmp
    fs.unlinkSync(file.path);

    res.status(200).json({
      webViewLink: (publicUrl as any).data.webViewLink,
      webContentLink: (publicUrl as any).data.webContentLink,
    });
  } catch (error) {
    console.error("Error uploading file:", error);
    res.status(500).json({ error: "Internal server error" });
  }
};

export default handler;
