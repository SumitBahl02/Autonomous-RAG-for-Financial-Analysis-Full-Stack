"use client";

import React, { useState } from "react";
import { AppSidebar } from "@/components/app-sidebar";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Separator } from "@/components/ui/separator";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import ChatCanvas from "@/components/chatWindow/ChatBackground";
import Navbar from "@/components/landingPage/navbar/Navbar";
import AiChat from "@/components/chatWindow/AIChat";
import Flow from "@/components/chatWindow/Tree";
import { Button } from "@/components/ui/button";
import { Loader2 } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import Link from "next/link"

function UploadWindow() {
  const [file, setFile] = useState<File | null>(null);
  const [uploadUrl, setUploadUrl] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const { toast } = useToast();

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    // Set the dropEffect to show the user what will happen
    e.dataTransfer.dropEffect = "copy";
  };

  const handleFileDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
      // Clear the drag data
      e.dataTransfer.clearData();
    }
  };

  const handleFileUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    setIsUploading(true);
    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const data = await response.json();
        setUploadUrl(data.webViewLink);
      } else {
        console.error("Upload failed:", await response.text());
      }
    } catch (error) {
      console.error("Error uploading file:", error);
    } finally {
      setIsUploading(false);
      toast({
        title: "Uplaod Done",
        description: "Please wait while we process your file",
        variant: "default",
        duration: 5000,
      });
    }
  };

  return (
    <div className="h-screen w-screen bg-[#030014] overflow-y-hidden overflow-x-scroll">
      <div className="ml-64">
        <Navbar type="chat" />
      </div>
      <SidebarProvider className="z-50 h-screen">
        <ChatCanvas />
        <AppSidebar className="z-40 absolute  bg-transparent" />
        <SidebarInset className=" z-40 bg-transparent ">
          <header className=" flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-[[data-collapsible=icon]]/sidebar-wrapper:h-12">
            <div className="flex items-center gap-2 px-4 ">
              <SidebarTrigger className="-ml-1  text-gray-300" />
              <Separator orientation="vertical" className="mr-2 h-4 " />
              <Breadcrumb>
                <BreadcrumbList>
                  <BreadcrumbItem className="hidden md:block ">
                    <BreadcrumbLink
                      href="#"
                      className="text-gray-200 hover:text-gray-500"
                    >
                      Data Source
                    </BreadcrumbLink>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator className="hidden md:block" />
                  <BreadcrumbItem>
                    <BreadcrumbPage className="text-white">
                      Upload Data
                    </BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
            </div>
          </header>
          <div className="flex flex-row ">
            <div className="flex flex-col items-center p-4 mx-auto">
              <div
                onDrop={handleFileDrop}
                onDragOver={handleDragOver}
                className="border-2 border-dashed rounded-3xl  border-gray-400 px-12 py-20 w-96 text-center"
              >
                {file ? (
                  <p className="text-gray-600">{file.name}</p>
                ) : (
                  <p className="text-gray-600">
                    Drag and drop a file here, or click the button below to
                    select one.
                  </p>
                )}
              </div>
              <AlertDialog>
                <AlertDialogTrigger><Button
                onClick={handleFileUpload}
                disabled={!file || isUploading}
                className="mt-8 bg-purple-600  px-6 py-2  text-white   disabled:opacity-50 rounded-xl"
              >
                {isUploading ? (
                  <div className="flex flex-row gap-4">
                    <Loader2 className="animate-spin" /> <p>"Uploading..."</p>
                  </div>
                ) : (
                  "Upload"
                )}
              </Button></AlertDialogTrigger>
                <AlertDialogContent className="bg-slate-100/10 backdrop-blur-md text-white border-transparent rounded-2xl">
                  <AlertDialogHeader>
                    <AlertDialogTitle>
                      Please wait while we process your file
                    </AlertDialogTitle>
                    <AlertDialogDescription>
                     After uploading the file, please wait a few minutes before starting a new chat while we process your file.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel className=" border-gray-600 bg-gray-600 text-gray-400 rounded-xl hover:bg-gray-500">Cancel</AlertDialogCancel>
                    <AlertDialogAction className="bg-white text-black rounded-xl hover:bg-gray-300">Continue</AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
              
              {uploadUrl && (
                <div className="mt-8">
                  <p className="text-purple-500 text-center mb-2">
                    File uploaded successfully! Public URL:
                  </p>
                  <Link
                    href={uploadUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-white underline hover:text-purple-300"
                  >
                    {uploadUrl}
                  </Link>
                </div>
              )}
            </div>
          </div>
        </SidebarInset>
      </SidebarProvider>
    </div>
  );
}

export default UploadWindow;
