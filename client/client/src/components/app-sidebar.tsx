"use client"

import * as React from "react"
import {
  AudioWaveform,
  BookOpen,
  Bot,
  Command,
  ChartBar,
  GalleryVerticalEnd,
  PlayIcon,
  GitGraphIcon,
  Settings2,
  SquareTerminal,
} from "lucide-react"

import { NavMain } from "@/components/nav-main"
import { NavProjects } from "@/components/nav-projects"
import { NavUser } from "@/components/nav-user"
import { TeamSwitcher } from "@/components/team-switcher"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarRail,
} from "@/components/ui/sidebar"

// This is sample data.
const data = {
  user: {
    name: "User",
    email: "user@example.com",
    avatar: "/vercel.svg",
  },
  teams: [
    {
      name: "Pathway",
      logo: GalleryVerticalEnd,
      plan: "Enterprise",
    },
    {
      name: "Dynamic AI",
      logo: AudioWaveform,
      plan: "Startup",
    },
  ],
  navMain: [
    {
      title: "Playground",
      url: "#",
      icon: SquareTerminal,
      isActive: true,
      items: [
        {
          title: "New Chat",
          url: "/chat",
        },
        {
          title: "Latest Replay",
          url: "/replay",
        },
      ],
    },
    {
      title: "Data Sources",
      url: "/upload",
      icon: BookOpen,
      items: [
        {
          title: "Upload docs",
          url: "/upload",
        }
      ],
    },
    {
      title: "Agents",
      url: "#",
      icon: Bot,
      items: [
        {
          title: "Finance",
          url: "#",
        },
        {
          title: "Math",
          url: "#",
        },
        {
          title: "Research",
          url: "#",
        },
      ],
    },
    {
      title: "Settings",
      url: "#",
      icon: Settings2,
      items: [
        {
          title: "General",
          url: "#",
        },
        {
          title: "Team",
          url: "#",
        },
        {
          title: "Billing",
          url: "#",
        },
        {
          title: "Limits",
          url: "#",
        },
      ],
    },
  ],
  projects: [
    {
      name: "Chatting",
      url: "#",
      icon: ChartBar,
    },
    {
      name: "Decision Tree",
      url: "#",
      icon: GitGraphIcon,
    },
    {
      name: "Chat Replay",
      url: "#",
      icon: PlayIcon,
    },
  ],
}

export function AppSidebar({ ...props }: React.ComponentProps<typeof Sidebar>) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarHeader>
        <TeamSwitcher teams={data.teams} />
      </SidebarHeader>
      <SidebarContent>
        <NavMain items={data.navMain} />
        <NavProjects projects={data.projects} />
      </SidebarContent>
      <SidebarFooter className="mb-1">
        <NavUser user={data.user} />
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  )
}
