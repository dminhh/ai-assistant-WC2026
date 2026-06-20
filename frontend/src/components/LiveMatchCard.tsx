// src/components/LiveMatchCard.tsx
import type { Match } from "@/lib/types"
import { PredictionBar } from "./PredictionBar"
import type { Prediction } from "@/lib/types"

interface Props { match: Match; prediction?: Prediction }

export function LiveMatchCard({ match, prediction }: Props) {
  return (
    <div className="relative bg-surface border border-border rounded-card p-7 overflow-hidden">
      {/* Subtle red glow */}
      <div className="absolute inset-0 bg-gradient-to-tr from-transparent to-red/5 pointer-events-none" />

      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <span className="inline-flex items-center gap-1.5 bg-red/15 border border-red/25 rounded-pill px-2.5 py-1 text-[11px] font-semibold tracking-widest text-red">
          <span className="w-1.5 h-1.5 rounded-full bg-red animate-pulse" />
          LIVE
        </span>
        <span className="font-mono text-xs text-text2">⏱ 67&apos; · MetLife Stadium</span>
      </div>

      {/* Scoreboard */}
      <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-5 mb-7">
        {/* Home */}
        <div className="flex flex-col gap-1.5">
          <span className="text-2xl">🇧🇷</span>
          <span className="font-display text-[32px] font-extrabold tracking-wide leading-none text-text">
            {match.home_team.toUpperCase()}
          </span>
          <span className="text-[11px] text-text3 tracking-widest">BẢNG G · H1</span>
        </div>

        {/* Score */}
        <div className="text-center">
          <span className="font-display text-[64px] font-extrabold leading-none text-text tracking-wide">
            {match.home_score ?? 0}
            <span className="text-text3 mx-1">–</span>
            {match.away_score ?? 0}
          </span>
        </div>

        {/* Away */}
        <div className="flex flex-col items-end gap-1.5">
          <span className="text-2xl">🇫🇷</span>
          <span className="font-display text-[32px] font-extrabold tracking-wide leading-none text-text">
            {match.away_team.toUpperCase()}
          </span>
          <span className="text-[11px] text-text3 tracking-widest">BẢNG G · H2</span>
        </div>
      </div>

      {/* Prediction bar */}
      {prediction && (
        <div className="border-t border-border pt-5">
          <PredictionBar
            home={prediction.home_win_prob}
            draw={prediction.draw_prob}
            away={prediction.away_win_prob}
            homeTeam={match.home_team}
            awayTeam={match.away_team}
            confidence={prediction.confidence}
            predictedScore={prediction.predicted_score}
          />
        </div>
      )}
    </div>
  )
}
