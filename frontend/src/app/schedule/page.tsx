// src/app/schedule/page.tsx
import { api } from "@/lib/api"
import { MatchCard } from "@/components/MatchCard"
import type { Match } from "@/lib/types"

export const revalidate = 60

function groupByDate(matches: Match[]): Record<string, Match[]> {
  const groups: Record<string, Match[]> = {}
  for (const m of matches) {
    // Convert UTC kickoff to ICT (UTC+7) date string
    const date = new Date(m.kickoff_time)
    const ictDate = new Date(date.getTime() + 7 * 60 * 60 * 1000)
    const key = ictDate.toISOString().slice(0, 10) // YYYY-MM-DD
    if (!groups[key]) groups[key] = []
    groups[key].push(m)
  }
  return groups
}

function formatDateLabel(dateStr: string): string {
  const date = new Date(dateStr + "T00:00:00+07:00")
  const today = new Date(new Date().getTime() + 7 * 60 * 60 * 1000)
  const todayStr = today.toISOString().slice(0, 10)
  const tomorrow = new Date(today.getTime() + 24 * 60 * 60 * 1000)
  const tomorrowStr = tomorrow.toISOString().slice(0, 10)

  if (dateStr === todayStr) return "Hôm nay"
  if (dateStr === tomorrowStr) return "Ngày mai"

  return date.toLocaleDateString("vi-VN", {
    weekday: "long",
    day: "2-digit",
    month: "2-digit",
  })
}

export default async function SchedulePage() {
  const [todayMatches, upcomingMatches, competitions] = await Promise.all([
    api.getTodayMatches().catch(() => []),
    api.getUpcomingMatches(30).catch(() => []),
    api.getCompetitions().catch(() => []),
  ])

  const activeComps = competitions.filter(c => c.is_active)

  // Merge today + upcoming, deduplicate by id
  const allMatches = [...todayMatches]
  const seenIds = new Set(todayMatches.map(m => m.id))
  for (const m of upcomingMatches) {
    if (!seenIds.has(m.id)) allMatches.push(m)
  }
  allMatches.sort((a, b) => new Date(a.kickoff_time).getTime() - new Date(b.kickoff_time).getTime())

  const grouped = groupByDate(allMatches)
  const sortedDates = Object.keys(grouped).sort()

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

      {sortedDates.length === 0 && activeComps.length > 0 && (
        <p className="text-center text-text2 py-20 text-sm">Không có lịch thi đấu sắp tới.</p>
      )}

      {sortedDates.map(dateStr => (
        <section key={dateStr} className="mb-10">
          <div className="flex items-center gap-3 mb-4">
            <span className="font-display text-[11px] font-bold tracking-[.14em] uppercase text-text3">
              {formatDateLabel(dateStr)}
            </span>
            <span className="text-[10px] text-text3">
              {new Date(dateStr + "T00:00:00+07:00").toLocaleDateString("vi-VN", {
                day: "2-digit",
                month: "2-digit",
                year: "numeric",
              })}
            </span>
            <div className="flex-1 h-px bg-border" />
          </div>

          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {grouped[dateStr].map(m => <MatchCard key={m.id} match={m} />)}
          </div>
        </section>
      ))}
    </div>
  )
}
