import { api } from "@/lib/api"
import { StandingsTable } from "@/components/StandingsTable"

export const revalidate = 300

export default async function StandingsPage() {
  const competitions = await api.getCompetitions().catch(() => [])
  const active = competitions.filter(c => c.is_active)

  // Fetch standings cho tất cả giải active song song
  const results = await Promise.all(
    active.map(async (comp) => {
      try {
        const tables = await api.getStandings(comp.api_competition_id)
        return { comp, tables }
      } catch {
        return { comp, tables: [] }
      }
    })
  )

  return (
    <div>
      <div className="mb-8">
        <h1 className="font-display text-3xl font-extrabold tracking-wide mb-1">Bảng xếp hạng</h1>
        <p className="text-sm text-text2">{active.length} giải đấu đang theo dõi</p>
      </div>

      {active.length === 0 && (
        <p className="text-center text-text2 py-20 text-sm">Chưa có giải đấu nào được kích hoạt.</p>
      )}

      {results.map(({ comp, tables }) => (
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

          {tables.length === 0 ? (
            <p className="text-sm text-text3 pl-1">Không có dữ liệu bảng xếp hạng.</p>
          ) : (
            <div className="space-y-4">
              {tables.map((table, i) => (
                <StandingsTable
                  key={i}
                  table={table}
                  label={tables.length > 1 ? `Bảng ${String.fromCharCode(65 + i)}` : undefined}
                />
              ))}
            </div>
          )}
        </section>
      ))}
    </div>
  )
}
