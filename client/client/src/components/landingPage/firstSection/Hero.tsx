import React from "react";
import HeroContentBox from "./HeroContentBox";

const Hero: React.FC = () => {
  return (
    <div className="relative flex flex-col h-full w-full" id="about-me">
      <video
        autoPlay
        muted
        loop
        className="rotate-180 absolute top-[-330px] h-full w-full left-0 z-[1] object-cover"
      >
        <source src="/blackhole.webm" type="video/webm" />
      </video>
      <div className="z-40">
        <HeroContentBox />
      </div>
    </div>
  );
};

export default Hero;