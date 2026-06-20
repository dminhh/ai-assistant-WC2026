"use client"
import type { Match } from "@/lib/types"

interface Props { matches: Match[] }

function buildItems(matches: Match[]) {
  return matches.flatMap((m) => {
    if (m.status === "live") {
      return [`🔴 ${m.home_team} ${m.home_score ?? 0}–${m.away_score ?? 0} ${m.away_team} (Đang diễn ra)`]
    }
    if (m.status === "finished") {
      return [`✅ ${m.home_team} ${m.home_score}–${m.away_score} ${m.away_team} (KT)`]
    }
    return []
  })
}

export function LiveTicker({ matches }: Props) {
  const items = buildItems(matches)
  if (items.length === 0) return null

  const doubled = [...items, ...items] // duplicate for seamless loop

  return (
    <div className="h-9 bg-surface border-b border-border flex items-center overflow-hidden">
      {/* Label */}
      <div className="flex-shrink-0 h-full bg-red px-3 flex items-center gap-1.5">
        <span className="w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
        <span className="font-display text-[11px] font-bold tracking-widest text-white">
          TRỰC TIẾP
        </span>
      </div>
      {/* Track */}
      <div className="overflow-hidden flex-1">
        <div
          className="flex gap-12 whitespace-nowrap px-6"
          style={{ animation: "ticker-scroll 30s linear infinite" }}
        >
          {doubled.map((item, i) => (
            <span key={i} className="text-xs text-text2">{item}</span>
          ))}
        </div>
      </div>
      <style>{`
        @keyframes ticker-scroll {
          from { transform: translateX(0); }
          to   { transform: translateX(-50%); }
        }
      `}</style>
    </div>
  )
}
