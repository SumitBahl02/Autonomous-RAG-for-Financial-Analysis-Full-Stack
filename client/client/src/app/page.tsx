import Hero from "@/components/landingPage/firstSection/Hero";
import Navbar from "@/components/landingPage/navbar/Navbar";
import StarsCanvas from "@/components/landingPage/StarBackground";
import Image from "next/image";

export default function Home() {
  return (
    <main className="h-full w-full bg-[#030014] overflow-y-auto overflow-x-hidden">
    <div className="flex flex-col gap-20">
     <StarsCanvas />
      <Navbar type = "home"/>
      <Hero/>
    </div>
    </main>
  );
}
