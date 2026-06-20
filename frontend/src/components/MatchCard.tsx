// src/components/MatchCard.tsx
import type { Match, Prediction } from "@/lib/types"
import { PredictionBar } from "./PredictionBar"

interface Props { match: Match; prediction?: Prediction }

function fmtTime(iso: string) {
  return new Date(iso).toLocaleTimeString("vi-VN", {
    hour: "2-digit", minute: "2-digit", timeZone: "Asia/Ho_Chi_Minh",
  }) + " ICT"
}

export function MatchCard({ match, prediction }: Props) {
  const isLive     = match.status === "live"
  const isFinished = match.status === "finished"

  return (
    <div className="group bg-surface border border-border rounded-card p-5 cursor-pointer transition-all duration-200 hover:-translate-y-0.5 hover:border-amber/30">
      {/* Top row */}
      <div className="flex justify-between items-center mb-4">
        <span className="font-mono text-xs text-text2">{fmtTime(match.kickoff_time)}</span>
        {isLive && (
          <span className="inline-flex items-center gap-1 bg-red/15 border border-red/25 rounded-pill px-2 py-0.5 text-[10px] font-bold tracking-widest text-red">
            <span className="w-1 h-1 rounded-full bg-red animate-pulse" />LIVE
          </span>
        )}
        {isFinished && <span className="text-[10px] text-text3">KẾT THÚC</span>}
        {!isLive && !isFinished && <span className="text-[10px] text-text3 tracking-wide">WC2026</span>}
      </div>

      {/* Teams */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex flex-col gap-1">
          <span className="text-xl">🇧🇷</span>
          <span className="font-display text-[18px] font-bold tracking-wide text-text">
            {match.home_team.toUpperCase()}
          </span>
        </div>

        <div className="text-center">
          {(isLive || isFinished) ? (
            <span className="font-display text-2xl font-bold text-text">
              {match.home_score}–{match.away_score}
            </span>
          ) : (
            <span className="text-xs text-text3 font-medium">vs</span>
          )}
        </div>

        <div className="flex flex-col items-end gap-1">
          <span className="text-xl">🇫🇷</span>
          <span className="font-display text-[18px] font-bold tracking-wide text-text">
            {match.away_team.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Prediction (upcoming only) */}
      {prediction && match.status === "upcoming" && (
        <div className="border-t border-border pt-4">
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
