import type { StandingEntry } from "@/lib/types"
import { getFlag } from "@/lib/teamFlags"

interface Props { table: StandingEntry[]; label?: string }

export function StandingsTable({ table, label }: Props) {
  return (
    <div className="rounded-card overflow-hidden" style={{ background: "linear-gradient(145deg, #0C1220, #0a1028)", border: "1px solid #1A2640" }}>
      {label && (
        <div className="px-4 py-2.5 border-b border-border">
          <span className="text-[11px] font-semibold tracking-widest text-text3 uppercase">{label}</span>
        </div>
      )}
      <div className="overflow-x-auto">
        <table className="w-full text-sm min-w-[400px]">
          <thead>
            <tr className="border-b border-border">
              <th className="text-left px-3 md:px-4 py-2.5 text-[10px] font-semibold tracking-widest text-text3 uppercase w-8">#</th>
              <th className="text-left px-2 py-2.5 text-[10px] font-semibold tracking-widest text-text3 uppercase">Đội</th>
              <th className="text-center px-2 py-2.5 text-[10px] font-semibold tracking-widest text-text3 uppercase">Trận</th>
              <th className="text-center px-2 py-2.5 text-[10px] font-semibold tracking-widest text-text3 uppercase">T</th>
              <th className="text-center px-2 py-2.5 text-[10px] font-semibold tracking-widest text-text3 uppercase">H</th>
              <th className="text-center px-2 py-2.5 text-[10px] font-semibold tracking-widest text-text3 uppercase">B</th>
              <th className="text-center px-2 py-2.5 text-[10px] font-semibold tracking-widest text-text3 uppercase">HS</th>
              <th className="text-center px-3 md:px-4 py-2.5 text-[10px] font-semibold tracking-widest text-amber uppercase">Đ</th>
            </tr>
          </thead>
          <tbody>
            {table.map((row, i) => (
              <tr key={row.position} className={`border-b border-border last:border-0 transition-colors hover:bg-surface2 ${i < 4 ? "border-l-2 border-l-green" : ""}`}>
                <td className="px-3 md:px-4 py-3 font-mono text-xs text-text3">{row.position}</td>
                <td className="px-2 py-3">
                  <span className="flex items-center gap-1.5 md:gap-2">
                    <span className="text-base flex-shrink-0">{getFlag(row.team.name)}</span>
                    <span className="font-medium text-text text-[12px] md:text-sm truncate">{row.team.name}</span>
                  </span>
                </td>
                <td className="px-2 py-3 text-center text-text2 font-mono text-xs">{row.playedGames}</td>
                <td className="px-2 py-3 text-center text-green font-mono text-xs">{row.won}</td>
                <td className="px-2 py-3 text-center text-text2 font-mono text-xs">{row.draw}</td>
                <td className="px-2 py-3 text-center text-red font-mono text-xs">{row.lost}</td>
                <td className="px-2 py-3 text-center text-text2 font-mono text-xs">{row.goalDifference > 0 ? `+${row.goalDifference}` : row.goalDifference}</td>
                <td className="px-3 md:px-4 py-3 text-center font-mono text-xs font-bold text-white">{row.points}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
