"use client"
// src/app/page.tsx
import { useEffect, useState, useCallback } from "react"
import { api } from "@/lib/api"
import { StatsRow } from "@/components/StatsRow"
import { LiveMatchCard } from "@/components/LiveMatchCard"
import { MatchCard } from "@/components/MatchCard"
import type { Match, Prediction, Competition } from "@/lib/types"

const REFRESH_INTERVAL = 30_000

export default function Dashboard() {
  const [matches, setMatches] = useState<Match[]>([])
  const [competitions, setCompetitions] = useState<Competition[]>([])
  const [predMap, setPredMap] = useState<Record<number, Prediction>>({})
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchData = useCallback(async () => {
    const [m, c] = await Promise.all([
      api.getTodayMatches().catch(() => [] as Match[]),
      api.getCompetitions().catch(() => [] as Competition[]),
    ])
    setMatches(m)
    setCompetitions(c)
    setLastUpdated(new Date())
    setLoading(false)

    const toPredict = m.filter(x => x.status === "live" || x.status === "upcoming")
    const entries = await Promise.all(
      toPredict.map(async (x) => {
        try {
          const p = await api.getPrediction(x.id)
          return [x.id, p] as [number, Prediction]
        } catch { return null }
      })
    )
    const map: Record<number, Prediction> = {}
    for (const e of entries) { if (e) map[e[0]] = e[1] }
    setPredMap(map)
  }, [])

  useEffect(() => {
    fetchData()
    const timer = setInterval(fetchData, REFRESH_INTERVAL)
    return () => clearInterval(timer)
  }, [fetchData])

  const live     = matches.filter(m => m.status === "live")
  const upcoming = matches.filter(m => m.status === "upcoming")
  const finished = matches.filter(m => m.status === "finished")
  const activeComps = competitions.filter(c => c.is_active)

  const stats = [
    { label: "Trận hôm nay",   value: String(matches.length), sub: `${live.length} đang diễn ra`, color: "text-amber" },
    { label: "Sắp diễn ra",    value: String(upcoming.length), sub: "trong 24 giờ tới" },
    { label: "Đã kết thúc",    value: String(finished.length), sub: "hôm nay", color: "text-green" },
    { label: "Giải đang theo", value: String(activeComps.length), sub: activeComps.map(c => c.name).join(" · ") || "Chưa có giải nào" },
  ]

  if (loading) return <DashboardSkeleton />

  return (
    <div className="animate-fade-in">
      {/* Header */}
      <div className="mb-8 flex items-end justify-between animate-fade-up">
        <div>
          <h1 className="font-display text-3xl font-extrabold tracking-wide mb-1">Dashboard</h1>
          <p className="text-sm text-text2">World Cup 2026 · Cập nhật liên tục</p>
        </div>
        {lastUpdated && (
          <span className="text-[11px] text-text3 tabular-nums">
            Cập nhật lúc {lastUpdated.toLocaleTimeString("vi-VN")}
          </span>
        )}
      </div>

      <div className="animate-fade-up" style={{ animationDelay: "60ms" }}>
        <StatsRow stats={stats} />
      </div>

      {/* Live */}
      {live.length > 0 && (
        <section className="mb-11 animate-fade-up" style={{ animationDelay: "120ms" }}>
          <Eyebrow>🔴 Đang diễn ra</Eyebrow>
          <div className="grid gap-4 md:grid-cols-2 stagger">
            {live.map(m => <LiveMatchCard key={m.id} match={m} prediction={predMap[m.id]} />)}
          </div>
        </section>
      )}

      {/* Upcoming */}
      {upcoming.length > 0 && (
        <section className="mb-11 animate-fade-up" style={{ animationDelay: "180ms" }}>
          <Eyebrow>⏰ Sắp diễn ra</Eyebrow>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3 stagger">
            {upcoming.map(m => <MatchCard key={m.id} match={m} prediction={predMap[m.id]} />)}
          </div>
        </section>
      )}

      {/* Finished */}
      {finished.length > 0 && (
        <section className="animate-fade-up" style={{ animationDelay: "240ms" }}>
          <Eyebrow>✅ Đã kết thúc</Eyebrow>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3 stagger">
            {finished.map(m => <MatchCard key={m.id} match={m} />)}
          </div>
        </section>
      )}

      {matches.length === 0 && (
        <p className="text-center text-text2 py-20 text-sm animate-fade-in">
          Hôm nay không có trận đấu nào.
        </p>
      )}
    </div>
  )
}

function DashboardSkeleton() {
  return (
    <div className="animate-fade-in">
      {/* Header skeleton */}
      <div className="mb-8 flex items-end justify-between">
        <div className="space-y-2">
          <div className="skeleton h-8 w-48" />
          <div className="skeleton h-4 w-64" />
        </div>
      </div>

      {/* Stats skeleton */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-9">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="rounded-card p-4 space-y-2" style={{ background: "#0C1220", border: "1px solid #1A2640" }}>
            <div className="skeleton h-3 w-20" />
            <div className="skeleton h-8 w-12" />
            <div className="skeleton h-3 w-28" />
          </div>
        ))}
      </div>

      {/* Cards skeleton */}
      <div className="mb-4">
        <div className="skeleton h-4 w-32 mb-4" />
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="rounded-card p-5 space-y-4" style={{ background: "#0C1220", border: "1px solid #1A2640" }}>
              <div className="flex justify-between">
                <div className="skeleton h-3 w-20" />
                <div className="skeleton h-3 w-12" />
              </div>
              <div className="flex items-center justify-between gap-2">
                <div className="flex flex-col items-center gap-2 flex-1">
                  <div className="skeleton h-8 w-8 rounded-full" />
                  <div className="skeleton h-3 w-16" />
                </div>
                <div className="skeleton h-6 w-10" />
                <div className="flex flex-col items-center gap-2 flex-1">
                  <div className="skeleton h-8 w-8 rounded-full" />
                  <div className="skeleton h-3 w-16" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
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
