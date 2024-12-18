"use client";

import React from "react";
import { motion } from "framer-motion";
import {
  slideInFromLeft,
  slideInFromRight,
  slideInFromTop,
} from "@/utils/motion";
import { SparklesIcon } from "@heroicons/react/24/solid";
import { Typewriter } from "react-simple-typewriter";
import Link from 'next/link'
import Image from "next/image";
import { Button } from "@/components/ui/button";

const HeroContentBox: React.FC = () => {
  return (
    <motion.div
      initial="hidden"
      animate="visible"
      className="flex flex-row px-20 w-full z-[20]"
    >
      <div className="h-full w-full flex flex-col gap-5 justify-center m-auto text-start">
        <motion.div variants={slideInFromTop} className="flex flex-row">
          <span className="Welcome-box py-[8px] px-[12px] border border-[#7042f88b] opacity-[0.9] flex flex-row rounded-3xl">
            <SparklesIcon className="text-[#b49bff] mr-[10px] h-5 w-5 flex" />
            <h1 className="Welcome-text text-[13px] text-[#b49bff] flex">
              Dynamic Multimodel RAG
            </h1>
          </span>
        </motion.div>

        <motion.div
          variants={slideInFromLeft(0.5)}
          className="flex flex-col text-6xl font-bold text-white max-w-[600px] w-auto h-auto"
        >
          <div className="pb-5 text-6xl font-medium text-start">
            Pathway to{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-purple-500 to-cyan-500">
              Productivity
            </span>
          </div>
          <span className="flex justify-start text-6xl font-medium">AI that</span>
          <code className="bg-muted relative rounded font-mono text-6xl font-medium text-transparent bg-clip-text bg-gradient-to-r from-purple-500 to-cyan-500">
            <Typewriter
              words={["{Thinks}", "{Reason}", "{Learns}", "{Grows}"]}
              typeSpeed={150}
              loop={0}
              cursor
              cursorStyle="|"
              cursorColor="white"
            />
          </code>
        </motion.div>

        <motion.p
          variants={slideInFromLeft(0.8)}
          className="text-lg text-gray-400 my-3 max-w-[600px]"
        >
          Pathway AI simplifies workflows and delivers smarter decisions with
          Retrieval-Augmented Generation. Automate processes and unlock
          real-time insights effortlessly.
        </motion.p>
        <Button  className="py-2 button-primary bg-transparenta text-center text-[#fffdfe] cursor-pointer rounded-lg max-w-[200px] shadow-inner shadow-purple-800 font-medium hover:shadow-purple-400">
        <Link href="/chat">
        <motion.a
          variants={slideInFromLeft(1)}
        >
          Try now!
        </motion.a>
        </Link>
        </Button>
      </div>

      <motion.div
        variants={slideInFromRight(0.8)}
        className="w-full h-full flex justify-center items-center"
      >
        <Image
          src="/mainIconsdark.svg"
          alt="work icons"
          height={400}
          width={400}
        />
      </motion.div>
    </motion.div>
  );
};

export default HeroContentBox;
