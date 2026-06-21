// src/components/PredictionBar.tsx
"use client"
import { useEffect, useRef } from "react"
import type { ScoreProb } from "@/lib/types"

interface Props {
  home:           number
  draw:           number
  away:           number
  homeTeam:       string
  awayTeam:       string
  confidence:     "low" | "medium" | "high"
  predictedScore: string | null
  scoreProbs?:    ScoreProb[] | null
}

const CONFIDENCE_LABEL = { low: "Thấp", medium: "Trung bình", high: "Cao" }
const CONFIDENCE_STYLE = {
  low:    { color: "#7A8FA8", background: "rgba(122,143,168,0.1)", border: "rgba(122,143,168,0.2)" },
  medium: { color: "#FFD700", background: "rgba(255,215,0,0.08)",  border: "rgba(255,215,0,0.2)" },
  high:   { color: "#2DC653", background: "rgba(45,198,83,0.08)",  border: "rgba(45,198,83,0.2)" },
}

export function PredictionBar({ home, draw, away, homeTeam, awayTeam, confidence, predictedScore, scoreProbs }: Props) {
  const homeRef = useRef<HTMLDivElement>(null)
  const drawRef = useRef<HTMLDivElement>(null)
  const awayRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const timeout = setTimeout(() => {
      if (homeRef.current) homeRef.current.style.width = `${home * 100}%`
      if (drawRef.current) drawRef.current.style.width = `${draw * 100}%`
      if (awayRef.current) awayRef.current.style.width = `${away * 100}%`
    }, 200)
    return () => clearTimeout(timeout)
  }, [home, draw, away])

  const fmt = (v: number) => `${Math.round(v * 100)}%`
  const maxProb = scoreProbs ? Math.max(...scoreProbs.map(s => s.prob)) : 0
  const cs = CONFIDENCE_STYLE[confidence]

  return (
    <div className="space-y-2.5">
      {/* Labels */}
      <div className="flex justify-between text-[11px] text-text3 tracking-wide">
        <span>{homeTeam} thắng</span>
        {predictedScore && (
          <span className="text-text3">
            Dự đoán: <span className="font-mono font-bold" style={{ color: "#FFD700" }}>{predictedScore}</span>
          </span>
        )}
        <span>{awayTeam} thắng</span>
      </div>

      {/* Bar */}
      <div className="flex h-2 rounded-full overflow-hidden gap-0.5">
        <div ref={homeRef}
          className="rounded-full transition-all duration-1000 ease-out"
          style={{ width: "0%", background: "linear-gradient(90deg, #2DC653, #1fa845)" }}
        />
        <div ref={drawRef}
          className="rounded-full transition-all duration-1000 ease-out"
          style={{ width: "0%", background: "#4A6080" }}
        />
        <div ref={awayRef}
          className="rounded-full transition-all duration-1000 ease-out"
          style={{ width: "0%", background: "linear-gradient(90deg, #3a7bd5, #4895EF)" }}
        />
      </div>

      {/* Values */}
      <div className="flex justify-between items-center">
        <div className="flex flex-col items-start">
          <span className="font-display text-xl font-bold leading-none" style={{ color: "#2DC653" }}>
            {fmt(home)}
          </span>
          <span className="text-[9px] text-text3 mt-0.5">thắng</span>
        </div>

        <div className="flex flex-col items-center gap-1.5">
          <div className="flex flex-col items-center">
            <span className="font-display text-xl font-bold leading-none text-slate">{fmt(draw)}</span>
            <span className="text-[9px] text-text3 mt-0.5">hòa</span>
          </div>
          <span className="text-[9px] font-semibold tracking-wide px-2 py-0.5 rounded-pill"
            style={{ color: cs.color, background: cs.background, border: `1px solid ${cs.border}` }}
          >
            ⚡ {CONFIDENCE_LABEL[confidence]}
          </span>
        </div>

        <div className="flex flex-col items-end">
          <span className="font-display text-xl font-bold leading-none" style={{ color: "#4895EF" }}>
            {fmt(away)}
          </span>
          <span className="text-[9px] text-text3 mt-0.5">thắng</span>
        </div>
      </div>

      {/* Score probability table */}
      {scoreProbs && scoreProbs.length > 0 && (
        <div className="mt-3 pt-3 space-y-1.5" style={{ borderTop: "1px solid rgba(255,255,255,0.06)" }}>
          <p className="text-[10px] tracking-widest uppercase mb-2" style={{ color: "#3A4F66" }}>
            Tỉ số có thể xảy ra
          </p>
          {scoreProbs.map(({ score, prob }) => (
            <div key={score} className="flex items-center gap-2">
              <span className="font-mono text-[12px] font-bold text-text w-8 shrink-0">{score}</span>
              <div className="flex-1 h-1 rounded-full overflow-hidden" style={{ background: "rgba(255,255,255,0.05)" }}>
                <div
                  className="h-full rounded-full transition-all duration-700"
                  style={{
                    width: `${(prob / maxProb) * 100}%`,
                    background: "linear-gradient(90deg, rgba(255,215,0,0.5), rgba(255,215,0,0.25))",
                  }}
                />
              </div>
              <span className="text-[11px] text-text2 font-mono w-10 text-right shrink-0">{prob}%</span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
