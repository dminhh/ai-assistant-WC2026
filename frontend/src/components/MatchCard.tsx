// src/components/MatchCard.tsx
"use client"
import type { Match, Prediction } from "@/lib/types"
import { PredictionBar } from "./PredictionBar"
import { getFlag } from "@/lib/teamFlags"

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
    <div
      className="group relative rounded-card p-5 cursor-pointer transition-all duration-250 hover:-translate-y-0.5 hover:shadow-gold overflow-hidden"
      style={{
        background: "linear-gradient(145deg, #0C1220 0%, #0a1028 100%)",
        border: "1px solid #1A2640",
      }}
    >
      {/* Subtle top accent */}
      <div className="absolute top-0 left-0 right-0 h-px opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        style={{ background: "linear-gradient(90deg, transparent, rgba(255,215,0,0.4), transparent)" }} />

      {/* Top row */}
      <div className="flex justify-between items-center mb-4">
        <span className="font-mono text-xs text-text2">{fmtTime(match.kickoff_time)}</span>
        {isLive && (
          <span className="inline-flex items-center gap-1 rounded-pill px-2 py-0.5 text-[10px] font-bold tracking-widest"
            style={{ background: "rgba(230,57,70,0.15)", border: "1px solid rgba(230,57,70,0.3)", color: "#E63946" }}
          >
            <span className="w-1 h-1 rounded-full bg-red animate-pulse" />LIVE
          </span>
        )}
        {isFinished && <span className="text-[10px] text-text3 tracking-wide">KẾT THÚC</span>}
        {!isLive && !isFinished && (
          <span className="text-[10px] tracking-widest font-semibold" style={{ color: "#3A4F66" }}>WC2026</span>
        )}
      </div>

      {/* Teams */}
      <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-2 mb-4">
        <div className="flex flex-col items-center gap-1.5 text-center">
          <span className="text-3xl">{getFlag(match.home_team)}</span>
          <span className="font-display text-[13px] font-bold tracking-wide text-text leading-tight break-words text-center w-full">
            {match.home_team.toUpperCase()}
          </span>
        </div>

        <div className="text-center px-2 shrink-0">
          {(isLive || isFinished) ? (
            <span className="font-display text-2xl font-extrabold"
              style={{ color: "#F0EDE4", textShadow: "0 0 12px rgba(255,215,0,0.15)" }}
            >
              {match.home_score}–{match.away_score}
            </span>
          ) : (
            <span className="text-xs text-text3 font-medium">vs</span>
          )}
        </div>

        <div className="flex flex-col items-center gap-1.5 text-center">
          <span className="text-3xl">{getFlag(match.away_team)}</span>
          <span className="font-display text-[13px] font-bold tracking-wide text-text leading-tight break-words text-center w-full">
            {match.away_team.toUpperCase()}
          </span>
        </div>
      </div>

      {/* Prediction (upcoming only) */}
      {prediction && match.status === "upcoming" && (
        <div className="border-t pt-4" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
          <PredictionBar
            home={prediction.home_win_prob}
            draw={prediction.draw_prob}
            away={prediction.away_win_prob}
            homeTeam={match.home_team}
            awayTeam={match.away_team}
            confidence={prediction.confidence}
            predictedScore={prediction.predicted_score}
            scoreProbs={prediction.score_probs}
          />
        </div>
      )}
    </div>
  )
}
