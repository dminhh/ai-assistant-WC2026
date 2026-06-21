"use client"
import Link from "next/link"
import Image from "next/image"
import { usePathname } from "next/navigation"
import { useEffect, useState } from "react"
import { isLoggedIn } from "@/lib/auth"

const LINKS = [
  { href: "/",            label: "Dashboard",    icon: "⊞" },
  { href: "/schedule",    label: "Lịch thi đấu", icon: "📅" },
  { href: "/standings",   label: "BXH",          icon: "🏆" },
  { href: "/predictions", label: "Dự đoán",      icon: "⚽" },
  { href: "/chat",        label: "AI Chat",      icon: "✦" },
]

export function Navbar() {
  const path = usePathname()
  const [loggedIn, setLoggedIn] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)

  useEffect(() => {
    setLoggedIn(isLoggedIn())
    setMenuOpen(false)
  }, [path])

  return (
    <nav className="sticky top-0 z-50" style={{
      background: "rgba(5,8,16,0.85)",
      backdropFilter: "blur(20px)",
      WebkitBackdropFilter: "blur(20px)",
      borderBottom: "1px solid rgba(255,215,0,0.08)",
      boxShadow: "0 4px 32px rgba(0,0,0,0.4)",
    }}>

      <div className="flex items-center h-16 md:h-[72px] px-4 md:px-8 gap-4 md:gap-8 max-w-[1400px] mx-auto">
        {/* Logo */}
        <Link href="/" className="flex-shrink-0 mr-2">
          <Image src="/wc2026-logo.png" alt="FIFA World Cup 2026" width={80} height={48} className="object-contain md:w-[100px] md:h-[60px]" />
        </Link>

        {/* Divider */}
        <div className="hidden md:block w-px h-7 bg-border flex-shrink-0" />

        {/* Desktop links */}
        <ul className="hidden md:flex gap-1 list-none flex-1">
          {LINKS.map(({ href, label, icon }) => {
            const active = path === href
            return (
              <li key={href}>
                <Link
                  href={href}
                  className={`flex items-center gap-1.5 text-[13px] font-medium tracking-wide transition-all duration-200 px-3.5 py-2 rounded-lg relative ${
                    active
                      ? "text-text"
                      : "text-text3 hover:text-text2 hover:bg-white/5"
                  }`}
                  style={active ? { background: "rgba(255,255,255,0.05)" } : {}}
                >
                  <span className="text-[11px] opacity-50">{icon}</span>
                  {label}
                  {active && (
                    <span className="absolute bottom-0 left-3 right-3 h-[2px] rounded-full bg-white/20" />
                  )}
                </Link>
              </li>
            )
          })}
        </ul>

        {/* Desktop right */}
        <div className="hidden md:flex ml-auto items-center gap-3 flex-shrink-0">
          <div className="flex items-center gap-1.5 text-[11px] text-text3 px-3 py-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-green animate-pulse" />
            LIVE
          </div>
          {loggedIn ? (
            <Link href="/admin"
              className={`text-[13px] font-medium px-3 py-1.5 rounded-lg transition-colors ${path === "/admin" ? "text-text bg-white/5" : "text-text3 hover:text-text hover:bg-white/5"}`}
            >
              ⚙ Admin
            </Link>
          ) : (
            <Link href="/login"
              className="text-[13px] font-medium text-text3 hover:text-text px-3 py-1.5 rounded-lg hover:bg-white/5 transition-colors"
            >
              Đăng nhập
            </Link>
          )}
        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden ml-auto flex flex-col gap-1.5 p-2 rounded-lg hover:bg-white/5"
          onClick={() => setMenuOpen(v => !v)}
          aria-label="Menu"
        >
          <span className={`block w-5 h-0.5 rounded-full bg-text2 transition-all duration-200 origin-center ${menuOpen ? "rotate-45 translate-y-2" : ""}`} />
          <span className={`block w-5 h-0.5 rounded-full bg-text2 transition-all duration-200 ${menuOpen ? "opacity-0 scale-x-0" : ""}`} />
          <span className={`block w-5 h-0.5 rounded-full bg-text2 transition-all duration-200 origin-center ${menuOpen ? "-rotate-45 -translate-y-2" : ""}`} />
        </button>
      </div>

      {/* Mobile menu */}
      {menuOpen && (
        <div className="md:hidden px-4 py-3 flex flex-col gap-1"
          style={{ borderTop: "1px solid rgba(255,215,0,0.08)", background: "rgba(5,8,16,0.98)" }}
        >
          {LINKS.map(({ href, label, icon }) => {
            const active = path === href
            return (
              <Link key={href} href={href}
                className={`flex items-center gap-3 text-[14px] font-medium py-3 px-3 rounded-xl transition-all ${
                  active ? "text-text" : "text-text2 hover:text-text hover:bg-white/5"
                }`}
                style={active ? { background: "rgba(255,255,255,0.06)" } : {}}
              >
                <span className="text-base">{icon}</span>
                {label}
                {active && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-gold" />}
              </Link>
            )
          })}
          <div className="mt-2 pt-2" style={{ borderTop: "1px solid rgba(255,255,255,0.05)" }}>
            {loggedIn ? (
              <Link href="/admin" className="flex items-center gap-3 text-[14px] font-medium py-3 px-3 text-text2 hover:text-text rounded-xl hover:bg-white/5">
                ⚙ Admin
              </Link>
            ) : (
              <Link href="/login" className="flex items-center gap-3 text-[14px] font-medium py-3 px-3 text-text2 hover:text-text rounded-xl hover:bg-white/5">
                Đăng nhập
              </Link>
            )}
          </div>
        </div>
      )}
    </nav>
  )
}
