"use client"

import * as React from "react"
import { NavUser } from "@/app/dashboard/components/nav-user"
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar"
import { Newspaper, Users } from "lucide-react"
import { User } from "next-auth"
import Link from "next/link"

// Navbar data that is.
const data = {
  navMain: [
    {
      title: "Menu",
      items: [
        {
          title: "Page 1",
          url: "/dashboard/page1",
          icon: Newspaper,
        },
        {
          title: "Page 2",
          url: "/dashboard/page2",
          icon: Users,
        },
      ],
    }
  ],
}

export function AppSidebar({ user, ...props }: React.ComponentProps<typeof Sidebar> & { user: User }) {
  return (
    <Sidebar collapsible="icon" {...props}>
      <SidebarContent>
        {data.navMain.map((item) => (
          <SidebarGroup key={item.title}>
            <SidebarGroupLabel>{item.title}</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {item.items.map((item) => (
                  <SidebarMenuItem key={item.title}>
                    <Link href={item.url} className="w-full">
                      <SidebarMenuButton tooltip={item.title}>
                        {item.icon && <item.icon />}
                        {item.title}
                      </SidebarMenuButton>
                    </Link>
                  </SidebarMenuItem>
                ))}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        ))}
      </SidebarContent>
      <SidebarFooter>
        <NavUser user={{
          name: user.name || '',
          email: user.email || '',
          avatar: user.image || '',
        }} />
      </SidebarFooter>
    </Sidebar>
  )
}
