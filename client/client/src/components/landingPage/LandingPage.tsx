import React from 'react'
import StarsCanvas from './StarBackground'
import Navbar from './navbar/Navbar'
import Hero from './firstSection/Hero'


function LandingPage() {
  return (
    <main className="h-full w-full bg-[#030014] overflow-y-scroll overflow-x-hidden">
    <div className="flex flex-col gap-20">
      <StarsCanvas/>
      <Navbar type = "home"/>
      <Hero/>
    </div>
    </main>
  )
}

export default LandingPage