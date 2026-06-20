// src/app/schedule/page.tsx
import { api }      from "@/lib/api"
import { MatchCard } from "@/components/MatchCard"
import type { Match } from "@/lib/types"

export const revalidate = 120

export default async function SchedulePage() {
  const [matches, competitions] = await Promise.all([
    api.getTodayMatches().catch(() => []),
    api.getCompetitions().catch(() => []),
  ])

  const activeComps = competitions.filter(c => c.is_active)

  // Group matches by competition
  const grouped: Record<number, Match[]> = {}
  for (const m of matches) {
    if (!grouped[m.competition_id]) grouped[m.competition_id] = []
    grouped[m.competition_id].push(m)
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="font-display text-3xl font-extrabold tracking-wide mb-1">Lịch thi đấu</h1>
        <p className="text-sm text-text2">{activeComps.length} giải đấu đang theo dõi</p>
      </div>

      {activeComps.length === 0 && (
        <p className="text-center text-text2 py-20 text-sm">
          Chưa có giải đấu nào được kích hoạt. Admin bật giải trong settings.
        </p>
      )}

      {activeComps.map(comp => {
        const compMatches = grouped[comp.id] ?? []
        return (
          <section key={comp.id} className="mb-10">
            <div className="flex items-center gap-3 mb-4">
              <span className="font-display text-[11px] font-bold tracking-[.14em] uppercase text-text3">
                {comp.name}
              </span>
              <span className="text-[10px] text-text3 bg-surface2 border border-border rounded-pill px-2 py-0.5">
                {comp.competition_type === "national" ? "ĐTQG" : "CLB"}
              </span>
              <div className="flex-1 h-px bg-border" />
            </div>

            {compMatches.length === 0 ? (
              <p className="text-sm text-text3 pl-1">Không có trận hôm nay.</p>
            ) : (
              <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
                {compMatches.map(m => <MatchCard key={m.id} match={m} />)}
              </div>
            )}
          </section>
        )
      })}
    </div>
  )
}
