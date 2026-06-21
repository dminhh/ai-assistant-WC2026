// src/components/LiveMatchCard.tsx
import type { Match, Prediction } from "@/lib/types"
import { PredictionBar } from "./PredictionBar"
import { getFlag } from "@/lib/teamFlags"

interface Props { match: Match; prediction?: Prediction }

export function LiveMatchCard({ match, prediction }: Props) {
  return (
    <div className="relative rounded-card overflow-hidden glow-red"
      style={{ background: "linear-gradient(145deg, #130a0c 0%, #0C1220 60%)", border: "1px solid rgba(230,57,70,0.25)" }}
    >
      <div className="absolute top-0 left-0 right-0 h-px"
        style={{ background: "linear-gradient(90deg, transparent, rgba(230,57,70,0.6), transparent)" }} />

      <div className="p-4 md:p-7">
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <span className="inline-flex items-center gap-1.5 rounded-pill px-3 py-1 text-[11px] font-bold tracking-widest"
            style={{ background: "rgba(230,57,70,0.15)", border: "1px solid rgba(230,57,70,0.3)", color: "#E63946" }}
          >
            <span className="w-1.5 h-1.5 rounded-full bg-red animate-pulse" />
            LIVE
          </span>
          <span className="font-mono text-xs text-text2">
            {match.minute != null ? `⏱ ${match.minute}'` : "⏱ LIVE"}
          </span>
        </div>

        {/* Scoreboard */}
        <div className="grid grid-cols-[1fr_auto_1fr] items-center gap-2 md:gap-5 mb-6">
          <div className="flex flex-col items-center gap-1.5 text-center min-w-0">
            <span className="text-3xl md:text-5xl">{getFlag(match.home_team)}</span>
            <span className="font-display text-[13px] md:text-[20px] font-extrabold tracking-wide leading-tight text-text break-words w-full">
              {match.home_team.toUpperCase()}
            </span>
          </div>

          <div className="text-center px-1 md:px-3 shrink-0">
            <div className="font-display font-extrabold leading-none tracking-wide text-[40px] md:text-[64px]"
              style={{ textShadow: "0 0 30px rgba(255,215,0,0.2)", color: "#F0EDE4" }}
            >
              {match.home_score ?? 0}
              <span className="text-text3 mx-1 md:mx-2">–</span>
              {match.away_score ?? 0}
            </div>
          </div>

          <div className="flex flex-col items-center gap-1.5 text-center min-w-0">
            <span className="text-3xl md:text-5xl">{getFlag(match.away_team)}</span>
            <span className="font-display text-[13px] md:text-[20px] font-extrabold tracking-wide leading-tight text-text break-words w-full">
              {match.away_team.toUpperCase()}
            </span>
          </div>
        </div>

        {/* Prediction bar */}
        {prediction && (
          <div className="border-t pt-4 md:pt-5" style={{ borderColor: "rgba(255,255,255,0.06)" }}>
            <p className="text-[10px] tracking-widest uppercase mb-3" style={{ color: "#3A4F66" }}>
              ⚽ Dự đoán trước trận
            </p>
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
    </div>
  )
}
