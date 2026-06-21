import type { Metadata } from "next"
import "./globals.css"
import { Navbar } from "@/components/Navbar"
import { AnimatedBackground } from "@/components/AnimatedBackground"

export const metadata: Metadata = {
  title: "WC2026 — Dự đoán bóng đá bằng AI",
  description: "Live scores, AI predictions và AI chat cho World Cup 2026",
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="vi" className="dark">
      <body>
        <AnimatedBackground />
        <div className="relative z-10">
          <Navbar />
          <main className="max-w-[1100px] mx-auto px-4 md:px-6 py-6 md:py-9 pb-20">
            {children}
          </main>
        </div>
      </body>
    </html>
  )
}
