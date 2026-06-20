import type { StandingEntry } from "@/lib/types"

interface Props {
  table: StandingEntry[]
  label?: string
}

export function StandingsTable({ table, label }: Props) {
  return (
    <div className="bg-surface border border-border rounded-card overflow-hidden">
      {label && (
        <div className="px-4 py-2.5 border-b border-border">
          <span className="text-[11px] font-semibold tracking-widest text-text3 uppercase">{label}</span>
        </div>
      )}
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border">
            <th className="text-left px-4 py-2.5 text-[10px] font-semibold tracking-widest text-text3 uppercase w-8">#</th>
            <th className="text-left px-2 py-2.5 text-[10px] font-semibold tracking-widest text-text3 uppercase">Đội</th>
            <th className="text-center px-2 py-2.5 text-[10px] font-semibold tracking-widest text-text3 uppercase">Trận</th>
            <th className="text-center px-2 py-2.5 text-[10px] font-semibold tracking-widest text-text3 uppercase">T</th>
            <th className="text-center px-2 py-2.5 text-[10px] font-semibold tracking-widest text-text3 uppercase">H</th>
            <th className="text-center px-2 py-2.5 text-[10px] font-semibold tracking-widest text-text3 uppercase">B</th>
            <th className="text-center px-2 py-2.5 text-[10px] font-semibold tracking-widest text-text3 uppercase">HS</th>
            <th className="text-center px-4 py-2.5 text-[10px] font-semibold tracking-widest text-amber uppercase">Đ</th>
          </tr>
        </thead>
        <tbody>
          {table.map((row, i) => (
            <tr key={row.position} className={`border-b border-border last:border-0 transition-colors hover:bg-surface2 ${i < 4 ? "border-l-2 border-l-green" : ""}`}>
              <td className="px-4 py-3 font-mono text-xs text-text3">{row.position}</td>
              <td className="px-2 py-3 font-medium text-text">{row.team.name}</td>
              <td className="px-2 py-3 text-center text-text2 font-mono text-xs">{row.playedGames}</td>
              <td className="px-2 py-3 text-center text-green font-mono text-xs">{row.won}</td>
              <td className="px-2 py-3 text-center text-text2 font-mono text-xs">{row.draw}</td>
              <td className="px-2 py-3 text-center text-red font-mono text-xs">{row.lost}</td>
              <td className="px-2 py-3 text-center text-text2 font-mono text-xs">{row.goalDifference > 0 ? `+${row.goalDifference}` : row.goalDifference}</td>
              <td className="px-4 py-3 text-center font-display text-base font-bold text-amber">{row.points}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
