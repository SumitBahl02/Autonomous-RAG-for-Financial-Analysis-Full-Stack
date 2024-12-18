import React from 'react'
import { Button } from "@/components/ui/button"
import { CoinsIcon } from "lucide-react"


function ChatNavbar() {
  return (
    <div>
     <Button>
      <CoinsIcon /><span className='font-semibold text-lg'>123456</span>   Tokens Used
    </Button>
    </div>
  )
}

export default ChatNavbar