"use client";

import React, { useState, useEffect } from "react";
import { io, Socket } from "socket.io-client";
import { SendHorizonalIcon } from "lucide-react";
import Lottie from "react-lottie";
import ChatLoader from "../../../public/chatLoader.json";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { format } from "date-fns";
import { Badge } from "@/components/ui/badge";
import { db } from "@/firebase/firebase";
import { collection, addDoc, serverTimestamp } from "firebase/firestore";

interface ChatMessage {
  id: number;
  timestamp: number;
  username: string;
  isAgent: boolean;
  parentAgent: string | null;
  content: string;
  thought: string;
  isUser: boolean;
  verdict: string;
  avatar?: string;
}

interface AiChatProps {
  type: string;
  onButtonClick: () => void;
  onChatUpdate: (chat: ChatMessage[]) => void; // Updated to provide the full chat history
  saveSignal: boolean;
  handleDoneSaveChat: () => void;
}

const AiChat: React.FC<AiChatProps> = ({
  type,
  onButtonClick,
  onChatUpdate,
  saveSignal,
  handleDoneSaveChat,
}) => {
  const [newMessage, setNewMessage] = useState("");
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [socket, setSocket] = useState<Socket | null>(null);

  // Save chat history to Firestore
  const saveChatToFirestore = async () => {
    try {
      const chatCollection = collection(db, "chatHistories");
      await addDoc(chatCollection, {
        history: chatHistory,
        servertimestamp: serverTimestamp(),
      });
      console.log("Chat history saved successfully!");
    } catch (error) {
      console.error("Error saving chat history:", error);
    } finally {
      handleDoneSaveChat();
      console.log("Save Chat done");
    }
  };

  // Initialize and manage socket connection
  useEffect(() => {
    const newSocket = io("http://172.30.2.194:5000", {
      withCredentials: true,
    });

    newSocket.on("connect", () => {
      console.log("Connected to socket server:", newSocket.id);
    });

    newSocket.on("update", (data) => {
      console.log("Incoming data", data);
      setChatHistory((prevChat) => [
        ...prevChat,
        {
          id: prevChat.length + 1,
          username: data.username,
          isAgent: data.isAgent,
          parentAgent: data.parentAgent,
          content: data.content,
          thought: data.thought,
          isUser: false,
          verdict: data.verdict,
          timestamp: new Date().getTime(),
        },
      ]);
    });

    newSocket.on("end-stream", () => {
      console.log("Stream ended, disconnecting socket...");
      newSocket.disconnect();
      setSocket(null);
      setLoading(false);
    });

    setSocket(newSocket);

    return () => {
      newSocket.disconnect();
      console.log("Socket disconnected");
    };
  }, []);

  // Save chat when the saveSignal changes
  useEffect(() => {
    if (saveSignal) {
      saveChatToFirestore();
    }
  }, [saveSignal]);

  // Call onChatUpdate whenever chatHistory changes
  useEffect(() => {
    onChatUpdate(chatHistory);
  }, [chatHistory, onChatUpdate]);

  // Send message handler
  const sendMessage = () => {
    if (!newMessage.trim()) return;

    onButtonClick();
    setLoading(true);

    const message: ChatMessage = {
      id: chatHistory.length + 1,
      content: newMessage,
      timestamp: new Date().getTime(),
      isUser: true,
      username: "You",
      isAgent: false,
      parentAgent: null,
      thought: "",
      verdict: "",
    };

    setChatHistory([...chatHistory, message]);
    setNewMessage("");

    if (socket) {
      socket.emit("simulate-chat", { query: newMessage });
    }
  };

  return (
    <div className="flex flex-col w-full border-transparent rounded-lg mr-auto ml-5 h-screen bg-white/20 backdrop-blur-sm">
      <div className="p-4 space-y-4 flex flex-col overflow-auto overflow-y-scroll mb-36 h-screen">
        {chatHistory.map((msg) => (
          <div key={msg.id}>
            <div
              className={`flex ${
                msg.isUser ? "justify-end" : "justify-start"
              } items-end space-x-2`}
            >
              {!msg.isUser && (
                <img
                  src="/coin.png"
                  alt="avatar"
                  className="w-10 object-cover h-10 rounded-full"
                />
              )}
              <div
                className={`rounded-xl px-4 py-2 shadow-2xl shadow-[#131213] ${
                  msg.isUser
                    ? "bg-purple-800 text-white"
                    : "bg-black text-white"
                }`}
              >
                <div className="flex flex-row gap-2">
                  <p className="font-bold flex">{msg.username}</p>
                  <span className="flex rounded-md">
                    {msg.isAgent ? (
                      <Badge variant="secondary" className="rounded-md">
                        Agent
                      </Badge>
                    ) : (
                      !msg.isUser && (
                        <Badge variant="secondary" className="rounded-md">
                          {msg.parentAgent}'s Tool
                        </Badge>
                      )
                    )}
                  </span>
                </div>
                <p>{msg.content}</p>
                {!msg.isUser && msg.thought && (
                  <Accordion type="single" collapsible>
                    <AccordionItem value="item-1">
                      <AccordionTrigger className="font-semibold">
                        Thought
                      </AccordionTrigger>
                      <AccordionContent>{msg.thought}</AccordionContent>
                    </AccordionItem>
                  </Accordion>
                )}
                <p className="text-xs mt-1">
                  {format(new Date(msg.timestamp), "p")}
                </p>
              </div>
            </div>
            <div>
              {loading && !msg.isUser ? (
                <div className="flex flex-row items-center justify-center">
                  <div className="flex">
                    <Lottie
                      options={{
                        loop: true,
                        autoplay: true,
                        animationData: ChatLoader,
                      }}
                      height={40}
                      width={40}
                    />
                  </div>
                </div>
              ) : (
                <p className="flex text-gray-400 text-center justify-center my-2">
                  {msg.verdict}
                </p>
              )}
            </div>
          </div>
        ))}
      </div>
      <div className="p-4 border-t-2 border-black sticky bottom-0 flex">
        <input
          className="flex-grow p-2 mr-4 border-gray-500 rounded bg-black text-white"
          placeholder="Type your message here…"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
        />
        <button
          className="py-2 px-6 bg-purple-900 text-white rounded hover:bg-blue-600 transition duration-150"
          disabled={!newMessage.trim()}
          onClick={sendMessage}
        >
          <SendHorizonalIcon />
        </button>
      </div>
    </div>
  );
};

export default AiChat;
