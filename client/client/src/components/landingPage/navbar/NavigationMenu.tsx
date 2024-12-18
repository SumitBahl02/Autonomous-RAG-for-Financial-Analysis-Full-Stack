import React from "react";
import { cn } from "@/lib/utils"; // Ensure the `cn` utility is imported correctly
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";

// Define types for the components array items
interface Component {
  title: string;
  href: string;
  description: string;
}

const components: Component[] = [
  {
    title: "Multi-Agent RAG Architecture",
    href: "/docs/primitives/alert-dialog",
    description:
      "Explore our hybrid system design balancing retrieval and contextual reasoning.",
  },
  {
    title: "LightRAG & GraphRAG Integration",
    href: "/docs/primitives/hover-card",
    description:
      "Delve into our enhanced data access models for complex financial datasets.",
  },
  {
    title: "FinGPT Integration",
    href: "/docs/primitives/progress",
    description:
      "Learn how our system leverages a specialized financial language model for precise terminology handling.",
  },
  {
    title: "Dynamic Data Adaptation",
    href: "/docs/primitives/scroll-area",
    description: "See how the system optimizes performance in evolving financial data environments.",
  },
  {
    title: "Schedulers, Guardrails & Fallbacks",
    href: "/docs/primitives/tabs",
    description:
      "Understand the mechanisms ensuring robustness, reliability, and controlled responses.",
  },
  {
    title: "Performance & Accuracy",
    href: "/docs/primitives/tooltip",
    description:
      "Review results from initial tests showcasing improved data retrieval and analysis accuracy.",
  },
];

export function NavigationMenuDemo() {
  return (
    <NavigationMenu>
      <NavigationMenuList>
        <NavigationMenuItem>
          <NavigationMenuTrigger className="bg-transparent backdrop-blur-md hover:backdrop-blur-lg hover:bg-transparent focus:backdrop-blur-lg focus:bg-transparent text-[#fefeff]">
            Getting started
          </NavigationMenuTrigger>
          <NavigationMenuContent>
            <ul className="grid gap-3 p-6 md:w-[400px] lg:w-[500px] lg:grid-cols-[.75fr_1fr] ">
              <li className="row-span-3">
                <NavigationMenuLink asChild>
                  <div
                    className="flex h-full w-full select-none flex-col justify-end rounded-md bg-white/40 bg-gradient-to-b from-muted/50 to-muted p-6 no-underline outline-none focus:shadow-md"
                  >
                    <FrameIcon className="size-6" />
                    <div className="mb-2 mt-4 text-lg font-medium text-black">
                      Pathway
                    </div>
                    <p className="text-sm leading-tight text-muted-foreground text-neutral-600">
                    Cutting-edge financial insights you can trust—seamless, adaptive, and built to evolve with your data.
                    </p>
                  </div>
                </NavigationMenuLink>
              </li>
              <ListItem href="/docs" title="Introduction">
                Chat with our  multiagent model.
              </ListItem>
              <ListItem href="/docs/installation" title="Installation">
                Realtime Decision tree.
              </ListItem>
              <ListItem href="/docs/primitives/typography" title="Typography">
                Dynamically Upload your data and get started.
              </ListItem>
            </ul>
          </NavigationMenuContent>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <NavigationMenuTrigger className="bg-transparent backdrop-blur-md hover:backdrop-blur-lg hover:bg-transparent focus:backdrop-blur-lg focus:bg-transparent text-[#fefeff]">
            Components
          </NavigationMenuTrigger>
          <NavigationMenuContent>
            <ul className="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2 lg:w-[600px]">
              {components.map((component) => (
                <ListItem
                  key={component.title}
                  title={component.title}
                  href={component.href}
                >
                  {component.description}
                </ListItem>
              ))}
            </ul>
          </NavigationMenuContent>
        </NavigationMenuItem>
        <NavigationMenuItem>
          <div className="text-[#fefeff]">
            <NavigationMenuLink className={navigationMenuTriggerStyle()}>
              Documentation
            </NavigationMenuLink>
          </div>
        </NavigationMenuItem>
      </NavigationMenuList>
    </NavigationMenu>
  );
}

interface ListItemProps {
  className?: string;
  title: string;
  children: React.ReactNode;
  href: string;
}

const ListItem = React.forwardRef<HTMLAnchorElement, ListItemProps>(
  ({ className, title, children, href, ...props }, ref) => {
    return (
      <li>
        <NavigationMenuLink asChild>
          <div
            className={cn(
              "block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-white/20 hover:backdrop-blur-3xl hover:shadow-2xl hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground",
              className
            )}
            {...props}
          >
            <div className="text-sm leading-none text-[#fefeff] font-semibold">{title}</div>
            <p className="line-clamp-2 text-sm leading-snug text-muted-foreground text-[#d1cfcf] ">
              {children}
            </p>
          </div>
        </NavigationMenuLink>
      </li>
    );
  }
);
ListItem.displayName = "ListItem";

function FrameIcon(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      color="black"
    >
      <line x1="22" x2="2" y1="6" y2="6" />
      <line x1="22" x2="2" y1="18" y2="18" />
      <line x1="6" x2="6" y1="2" y2="22" />
      <line x1="18" x2="18" y1="2" y2="22" />
    </svg>
  );
}
