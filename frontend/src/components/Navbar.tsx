"use client"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useEffect, useState } from "react"
import { isLoggedIn } from "@/lib/auth"

const LINKS = [
  { href: "/",            label: "Dashboard" },
  { href: "/schedule",    label: "Lịch thi đấu" },
  { href: "/standings",   label: "BXH" },
  { href: "/predictions", label: "Dự đoán" },
  { href: "/chat",        label: "AI Chat" },
]

export function Navbar() {
  const path = usePathname()
  const [loggedIn, setLoggedIn] = useState(false)

  useEffect(() => {
    setLoggedIn(isLoggedIn())
  }, [path])

  return (
    <nav className="sticky top-0 z-50 h-14 flex items-center gap-10 px-6 border-b border-border"
         style={{ background: "rgba(10,14,26,.92)", backdropFilter: "blur(12px)" }}>
      {/* Logo */}
      <span className="font-display text-[22px] font-extrabold tracking-wide">
        WC<span className="text-amber">2026</span>
      </span>

      {/* Links */}
      <ul className="flex gap-7 list-none flex-1">
        {LINKS.map(({ href, label }) => {
          const active = path === href
          return (
            <li key={href}>
              <Link
                href={href}
                className={`text-[13px] font-medium tracking-wide transition-colors relative pb-[18px] ${
                  active ? "text-amber" : "text-text2 hover:text-text"
                }`}
              >
                {label}
                {active && (
                  <span className="absolute bottom-0 left-0 right-0 h-[2px] bg-amber rounded-sm" />
                )}
              </Link>
            </li>
          )
        })}
      </ul>

      {/* Right side */}
      <div className="ml-auto flex items-center gap-3">
        {loggedIn ? (
          <Link
            href="/admin"
            className={`text-[13px] font-medium tracking-wide transition-colors ${
              path === "/admin" ? "text-amber" : "text-text2 hover:text-text"
            }`}
          >
            ⚙ Admin
          </Link>
        ) : (
          <Link
            href="/login"
            className="text-[13px] font-medium text-text2 hover:text-text transition-colors"
          >
            Đăng nhập
          </Link>
        )}
        <Link
          href="/chat"
          className="bg-amber text-base text-[13px] font-semibold rounded-pill px-4 py-1.5 transition-opacity hover:opacity-85"
        >
          ⚡ Hỏi AI
        </Link>
      </div>
    </nav>
  )
}
