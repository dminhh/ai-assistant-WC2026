import type { Metadata } from "next"
import "./globals.css"
import { Navbar }     from "@/components/Navbar"
import { LiveTicker } from "@/components/LiveTicker"
import { api }        from "@/lib/api"

export const metadata: Metadata = {
  title: "WC2026 — Dự đoán bóng đá bằng AI",
  description: "Live scores, AI predictions và AI chat cho World Cup 2026",
}

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  const matches = await api.getTodayMatches().catch(() => [])

  return (
    <html lang="vi" className="dark">
      <body>
        <LiveTicker matches={matches} />
        <Navbar />
        <main className="max-w-[1100px] mx-auto px-6 py-9 pb-20">
          {children}
        </main>
      </body>
    </html>
  )
}
