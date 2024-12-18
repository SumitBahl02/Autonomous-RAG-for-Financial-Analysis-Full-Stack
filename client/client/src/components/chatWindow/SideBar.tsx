"use client";
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
import StarsCanvas from "../landingPage/StarBackground";
import ChatCanvas from "./ChatBackground";
import Navbar from "../landingPage/navbar/Navbar";
import AiChat from "./AIChat";
import Flow from "./Tree";
import { Button } from "@/components/ui/button";
import Lottie from "react-lottie";
import ChatLoader from "../../../public/chatLoader.json"; // Adjust the path to your ChatLoader.json file
import { useToast } from "@/hooks/use-toast"

const SideBar = () => {
  const [signal, setSignal] = useState<number | null>(null);
  const [chat, setChat] = useState<any[]>([]);
  const [saveSignal, setsaveSignal] = useState<boolean>(false);
  const { toast } = useToast()
    const handleButtonClick = () => {
        setSignal(Date.now()); // Generate a unique signal using timestamp
      };
    
      const handleSignalProcessed = () => {
        setSignal(null); // Clear the signal after it's processed
      };

      const handleChatUpdate = (chatData: any[]) => {
        setChat(chatData); // Update the chat array in the parent
      };

      const handleSaveChat = () => {
        console.log("Save Chat signal triggered");
        setsaveSignal(true);
        // Trigger the saveChat function in AiChat
      };
      const handleDoneSaveChat = () => {
        console.log("Save Chat signal triggered");
        setsaveSignal(false);
        // Trigger the saveChat function in AiChat

        toast({
          title: "Chat saved",
          description: "Your chat has been saved successfully",
          variant: "default",
          duration: 5000,
        })

      };
  return (
    <div className="h-screen w-max bg-[#030014] overflow-y-hidden overflow-x-scroll">
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
                      New Chat
                    </BreadcrumbPage>
                  </BreadcrumbItem>
                </BreadcrumbList>
              </Breadcrumb>
              <Button className="rounded-2xl ml-4 hover:bg-gray-600" onClick={handleSaveChat}>
                {saveSignal ? (
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
                  "Save Chat"
                )}
              </Button>
            </div>
          </header>
          <div className="flex flex-row w-max">
            <div className="flex">
              <AiChat type = "chat" onButtonClick={handleButtonClick} onChatUpdate={handleChatUpdate} saveSignal={saveSignal} handleDoneSaveChat={handleDoneSaveChat}/>
            </div>
            <div className="flex overflow-x-scroll">
              <Flow type = "chat" signal={signal} onSignalProcessed={handleSignalProcessed} chat={chat}  />
            </div>
          </div>
        </SidebarInset>
      </SidebarProvider>
    </div>
  );
};

export default SideBar;
