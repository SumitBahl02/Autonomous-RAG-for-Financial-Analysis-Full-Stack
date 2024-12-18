"use client";
import React, { useState, useEffect } from "react";
import { SendHorizonalIcon } from "lucide-react";
import Lottie from "react-lottie";
import ChatLoader from "../../../public/chatLoader.json";
import { format } from "date-fns";
import { Badge } from "@/components/ui/badge";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { collection, query, orderBy, limit, getDocs } from "firebase/firestore";
import { db } from "@/firebase/firebase"; // Replace with your Firebase config file path
import { Button } from "../ui/button";
import { useToast } from "@/hooks/use-toast";

export default function ReplayAiChat({
  type,
  onButtonClick,
  onChatUpdate,
  replay,
  handleDoneReplay,
}: {
  type: string;
  onButtonClick: () => void;
  onChatUpdate: (chat: any[]) => void;
  replay: boolean;
  handleDoneReplay: () => void;
}) {
  const [newMessage, setNewMessage] = useState("");
  const [chatHistory, setChatHistory] = useState<
    {
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
    }[]
  >([]);
  const { toast } = useToast();
  const [chatIndex, setChatIndex] = useState(0);
  const [userInteracted, setUserInteracted] = useState(false);
  const [simulationStarted, setSimulationStarted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [initialChat, setInitialChat] = useState<any[]>([]);
  const [serverTimestamp, setServerTimestamp] = useState<string | null>(null);

  // Fetch the latest chat history from Firestore
  const fetchChatHistory = async () => {
    try {
      const chatCollection = collection(db, "chatHistories");
      const q = query(
        chatCollection,
        orderBy("servertimestamp", "desc"),
        limit(1)
      );
      const querySnapshot = await getDocs(q);

      if (!querySnapshot.empty) {
        const latestChat = querySnapshot.docs[0].data();
        setInitialChat(latestChat.history || []);
        onChatUpdate(latestChat.history || []);
        setServerTimestamp(
          latestChat.servertimestamp?.toDate()?.toLocaleString() || null
        );
      } else {
        console.warn("No chat history found.");
      }
    } catch (error) {
      console.error("Error fetching chat history:", error);
    }
  };

  // Effect to start the simulation when replay becomes true
  useEffect(() => {
    if (replay) {
      fetchChatHistory().then(() => {
        setSimulationStarted(true);
        onButtonClick();
        console.log("Initial chat", initialChat);
        setUserInteracted(true);
      });
    }
  }, [replay]);

  // Function to handle sending messages
  const sendMessage = () => {
    // if (!newMessage.trim()) return;

    // onButtonClick();
    // onChatUpdate(initialChat);
    // const message = {
    //   id: chatHistory.length + 1,
    //   content: newMessage,
    //   timestamp: new Date().getTime(),
    //   isUser: true,
    //   username: "You",
    //   isAgent: false,
    //   parentAgent: null,
    //   thought: "",
    //   verdict: "",
    // };
    // setChatHistory([...chatHistory, message]);
    // setNewMessage("");
    // setUserInteracted(true);
    // if (!simulationStarted) {
    //   setSimulationStarted(true);
    // }

    toast({
      title: "No messaging during replay",
      description: "Your Cant send messages during replay",
      variant: "destructive",
      duration: 2000,
    });
  };

  // Effect for simulating chat replay
  useEffect(() => {
    if (
      !simulationStarted ||
      (chatIndex >= initialChat.length && !userInteracted)
    ) {
      if (simulationStarted && chatIndex >= initialChat.length) {
        handleDoneReplay(); // Notify that the simulation has ended
        setSimulationStarted(false); // Reset the simulation state
      }
      return;
    }

    setLoading(true);
    const timer = setTimeout(() => {
      if (!userInteracted && chatIndex < initialChat.length) {
        setChatHistory((prevChat) => [
          ...prevChat,
          {
            ...initialChat[chatIndex],
            id: prevChat.length + 1,
            timestamp: new Date().getTime(),
          },
        ]);
        setChatIndex(chatIndex + 1);
      }
      setUserInteracted(false);
      setLoading(false);
    }, 3000);

    return () => clearTimeout(timer);
  }, [
    chatHistory,
    chatIndex,
    userInteracted,
    simulationStarted,
    initialChat,
    handleDoneReplay,
  ]);

  return (
    <div className="flex flex-col w-[700px] border-transparent bg-white/20 backdrop-blur-sm rounded-lg mr-auto ml-5 h-screen">
      <div className="p-4 space-y-4 flex flex-col overflow-auto overflow-y-scroll mb-36 h h-screen">
        {serverTimestamp && (
          <div className="text-center text-sm text-gray-500">
            Chat Timestamp: {serverTimestamp}
          </div>
        )}
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
                <div className="flex flex-row gap-2 ">
                  <p className="font-bold flex">{msg.username}</p>
                  <span className="flex rounded-md">
                    {msg.isAgent ? (
                      <Badge variant="secondary" className="rounded-md">
                        Agent
                      </Badge>
                    ) : (
                      <span>
                        {!msg.isUser ? (
                          <Badge variant="secondary" className="rounded-md">
                            {msg.parentAgent}'s Tool
                          </Badge>
                        ) : (
                          <div></div>
                        )}
                      </span>
                    )}
                  </span>
                </div>
                <p>{msg.content}</p>
                {!msg.isUser && msg.thought && msg.thought != null && (
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
                  {/* <p className="flex text-gray-400 text-center justify-center">
                    {msg.verdict} {" ..."}
                  </p> */}
                </div>
              ) : (
                <p className="flex text-gray-400 text-center justify-center my-2">
                  {/* {msg.verdict} */}
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
        <Button
          className="py-2 px-6  bg-purple-900 text-white rounded  transition duration-150"
          onClick={sendMessage}
        >
          <SendHorizonalIcon />
        </Button>
      </div>
    </div>
  );
}
