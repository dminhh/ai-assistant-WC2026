// src/components/PredictionBar.tsx
"use client"
import { useEffect, useRef } from "react"

interface Props {
  home:           number    // 0–1
  draw:           number
  away:           number
  homeTeam:       string
  awayTeam:       string
  confidence:     "low" | "medium" | "high"
  predictedScore: string | null
}

const CONFIDENCE_LABEL = { low: "Thấp", medium: "Trung bình", high: "Cao" }
const CONFIDENCE_COLOR = {
  low:    "text-text3  bg-surface2  border-border",
  medium: "text-amber  bg-amber/10  border-amber/20",
  high:   "text-green  bg-green/10  border-green/20",
}

export function PredictionBar({ home, draw, away, homeTeam, awayTeam, confidence, predictedScore }: Props) {
  const homeRef = useRef<HTMLDivElement>(null)
  const drawRef = useRef<HTMLDivElement>(null)
  const awayRef = useRef<HTMLDivElement>(null)

  // Animate bars from 0 on mount
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (homeRef.current) homeRef.current.style.width = `${home * 100}%`
      if (drawRef.current) drawRef.current.style.width = `${draw * 100}%`
      if (awayRef.current) awayRef.current.style.width = `${away * 100}%`
    }, 200)
    return () => clearTimeout(timeout)
  }, [home, draw, away])

  const fmt = (v: number) => `${Math.round(v * 100)}%`

  return (
    <div className="space-y-2">
      {/* Labels */}
      <div className="flex justify-between text-[11px] text-text3 tracking-wide">
        <span>{homeTeam} thắng</span>
        {predictedScore && (
          <span className="text-text3">
            Dự đoán: <span className="text-amber font-mono font-medium">{predictedScore}</span>
          </span>
        )}
        <span>{awayTeam} thắng</span>
      </div>

      {/* Bar */}
      <div className="flex h-1.5 rounded-full overflow-hidden gap-0.5">
        <div
          ref={homeRef}
          className="bg-green rounded-full transition-all duration-1000 ease-out"
          style={{ width: "0%" }}
        />
        <div
          ref={drawRef}
          className="bg-slate rounded-full transition-all duration-1000 ease-out"
          style={{ width: "0%" }}
        />
        <div
          ref={awayRef}
          className="bg-blue rounded-full transition-all duration-1000 ease-out"
          style={{ width: "0%" }}
        />
      </div>

      {/* Values */}
      <div className="flex justify-between items-center">
        <span className="font-display text-xl font-bold text-green leading-none">
          {fmt(home)}<sub className="font-body text-[9px] text-text3 font-normal ml-0.5">thắng</sub>
        </span>
        <div className="flex flex-col items-center gap-1">
          <span className="font-display text-xl font-bold text-slate leading-none">
            {fmt(draw)}<sub className="font-body text-[9px] text-text3 font-normal ml-0.5">hòa</sub>
          </span>
          <span className={`text-[9px] font-semibold tracking-wide px-2 py-0.5 rounded-pill border ${CONFIDENCE_COLOR[confidence]}`}>
            ⚡ Tin cậy {CONFIDENCE_LABEL[confidence]}
          </span>
        </div>
        <span className="font-display text-xl font-bold text-blue leading-none">
          {fmt(away)}<sub className="font-body text-[9px] text-text3 font-normal ml-0.5">thắng</sub>
        </span>
      </div>
    </div>
  )
}
