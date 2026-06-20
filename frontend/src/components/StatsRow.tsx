// src/components/StatsRow.tsx
interface Stat { label: string; value: string; sub: string; color?: string }

interface Props { stats: Stat[] }

export function StatsRow({ stats }: Props) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-9">
      {stats.map((s) => (
        <div key={s.label} className="bg-surface border border-border rounded-card p-4">
          <p className="text-[10px] font-semibold tracking-widest text-text3 uppercase mb-2">{s.label}</p>
          <p className={`font-display text-[32px] font-extrabold leading-none ${s.color ?? "text-text"}`}>
            {s.value}
          </p>
          <p className="text-[11px] text-text3 mt-1">{s.sub}</p>
        </div>
      ))}
    </div>
  )
}
