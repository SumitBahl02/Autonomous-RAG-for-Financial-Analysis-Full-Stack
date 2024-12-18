"use client"

import React, {useState} from "react";
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
import ReplayAiChat from "@/components/chatWindow/ReplayAiChat";
import ReplayFlow from "@/components/chatWindow/ReplayTree";
import { Button } from "@/components/ui/button";
import Lottie from "react-lottie";
import ChatLoader from "../../../public/chatLoader.json"; // Adjust the path to your ChatLoader.json file
import { useToast } from "@/hooks/use-toast"
import { Loader2 } from "lucide-react"


function ReplayWindow() {
    const [signal, setSignal] = useState<number | null>(null);
    const [chat, setChat] = useState<any[]>([]);
    const [replay, setReplay] = useState<boolean>(false);
    const { toast } = useToast()
    
    const handleButtonClick = () => {
        setSignal(Date.now()); // Generate a unique signal using timestamp
      };
    
      const handleReplay = () => {
        setReplay(true);
        console.log("Replay signal triggered");
      };

      const handleDoneReplay = () => {
        setReplay(false);
        console.log("Replay done");

        toast({
            title: "Replay Done",
            description: "Your chat has been replayed successfully",
            variant: "default",
            duration: 5000,
          })
      };

      const handleChatUpdate = (chatData: any[]) => {
        console.log("Chat updatedddddd", chatData);
        setChat(chatData); // Update the chat array in the parent
      };

      const handleSignalProcessed = () => {
        setSignal(null); // Clear the signal after it's processed
      };

  return (
    <div className="h-screen  w-max bg-[#030014] overflow-y-hidden overflow-x-scroll">
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
                      Playground
                    </BreadcrumbLink>
                  </BreadcrumbItem>
                  <BreadcrumbSeparator className="hidden md:block" />
                  <BreadcrumbItem>
                    <BreadcrumbPage className="text-white">
                      Latest Replay
                    </BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
              <Button className="rounded-2xl ml-4 hover:bg-gray-600" onClick={handleReplay}>
                {replay ? (
                <Lottie
                   options={{
                     loop: true,
                     autoplay: true,
                     animationData: ChatLoader,
                   }}
                   height={24}
                   width={24}
                 />
                ) : (
                  "Replay History"
                )}
              </Button>
            </div>
          </header>
          <div className="flex flex-row w-max">
            <div className="flex ">
              <ReplayAiChat type = "replay" onButtonClick={handleButtonClick} onChatUpdate={handleChatUpdate} replay={replay} handleDoneReplay={handleDoneReplay} />
            </div>
            <div className="flex overflow-x-scroll ">
              <ReplayFlow type = "replay" signal={signal} onSignalProcessed={handleSignalProcessed} chat={chat} />
            </div>
          </div>
        </SidebarInset>
      </SidebarProvider>
    </div>
  );
}

export default ReplayWindow;
