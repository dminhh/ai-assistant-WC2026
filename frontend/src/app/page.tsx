// src/app/page.tsx
import { api }           from "@/lib/api"
import { StatsRow }      from "@/components/StatsRow"
import { LiveMatchCard } from "@/components/LiveMatchCard"
import { MatchCard }     from "@/components/MatchCard"
import type { Prediction } from "@/lib/types"

export const revalidate = 60

export default async function Dashboard() {
  const matches = await api.getTodayMatches().catch(() => [])

  const live     = matches.filter(m => m.status === "live")
  const upcoming = matches.filter(m => m.status === "upcoming")
  const finished = matches.filter(m => m.status === "finished")

  // Fetch predictions cho upcoming matches (song song)
  const predMap: Record<number, Prediction> = {}
  await Promise.all(
    [...live, ...upcoming].map(async (m) => {
      try { predMap[m.id] = await api.getPrediction(m.id) } catch {}
    })
  )

  const stats = [
    { label: "Trận hôm nay",   value: String(matches.length), sub: `${live.length} đang diễn ra`,  color: "text-amber" },
    { label: "Sắp diễn ra",    value: String(upcoming.length), sub: "trong 24 giờ tới" },
    { label: "Đã kết thúc",    value: String(finished.length), sub: "hôm nay",                       color: "text-green" },
    { label: "Giải đang theo", value: "4",                     sub: "WC · PL · LaLiga · UCL" },
  ]

  return (
    <div>
      <div className="mb-8">
        <h1 className="font-display text-3xl font-extrabold tracking-wide mb-1">Dashboard</h1>
        <p className="text-sm text-text2">World Cup 2026 · Cập nhật liên tục</p>
      </div>

      <StatsRow stats={stats} />

      {/* Live */}
      {live.length > 0 && (
        <section className="mb-11">
          <Eyebrow>🔴 Đang diễn ra</Eyebrow>
          <div className="grid gap-4 md:grid-cols-2">
            {live.map(m => <LiveMatchCard key={m.id} match={m} prediction={predMap[m.id]} />)}
          </div>
        </section>
      )}

      {/* Upcoming */}
      {upcoming.length > 0 && (
        <section className="mb-11">
          <Eyebrow>⏰ Sắp diễn ra</Eyebrow>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {upcoming.map(m => <MatchCard key={m.id} match={m} prediction={predMap[m.id]} />)}
          </div>
        </section>
      )}

      {/* Finished */}
      {finished.length > 0 && (
        <section>
          <Eyebrow>✅ Đã kết thúc</Eyebrow>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {finished.map(m => <MatchCard key={m.id} match={m} />)}
          </div>
        </section>
      )}

      {matches.length === 0 && (
        <p className="text-center text-text2 py-20 text-sm">Hôm nay không có trận đấu nào.</p>
      )}
    </div>
  )
}

function Eyebrow({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex items-center gap-3 mb-4">
      <span className="text-[11px] font-semibold tracking-[.14em] uppercase text-text3">{children}</span>
      <div className="flex-1 h-px bg-border" />
    </div>
  )
}
