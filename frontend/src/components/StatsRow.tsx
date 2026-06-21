// src/components/StatsRow.tsx
interface Stat { label: string; value: string; sub: string; color?: string }

interface Props { stats: Stat[] }

export function StatsRow({ stats }: Props) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-9">
      {stats.map((s) => (
        <div
          key={s.label}
          className="relative rounded-card p-4 overflow-hidden group"
          style={{
            background: "linear-gradient(145deg, #0C1220, #0a1028)",
            border: "1px solid #1A2640",
          }}
        >
          {/* Hover accent */}
          <div className="absolute top-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-300"
            style={{ background: "linear-gradient(90deg, transparent, rgba(255,215,0,0.3), transparent)" }} />

          <p className="text-[10px] font-semibold tracking-widest uppercase mb-2" style={{ color: "#3A4F66" }}>
            {s.label}
          </p>
          <p className={`font-display text-[32px] font-extrabold leading-none ${s.color ?? "text-text"}`}
            style={!s.color ? { color: "#FFD700" } : undefined}
          >
            {s.value}
          </p>
          <p className="text-[11px] text-text3 mt-1">{s.sub}</p>
        </div>
      ))}
    </div>
  )
}
