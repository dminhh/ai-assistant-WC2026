// src/app/predictions/page.tsx
import { api }      from "@/lib/api"
import { MatchCard } from "@/components/MatchCard"
import type { Prediction } from "@/lib/types"

export const revalidate = 300

export default async function PredictionsPage() {
  const matches  = await api.getTodayMatches().catch(() => [])
  const upcoming = matches.filter(m => m.status === "upcoming")

  const predMap: Record<number, Prediction> = {}
  await Promise.all(
    upcoming.map(async m => {
      try { predMap[m.id] = await api.getPrediction(m.id) } catch {}
    })
  )

  return (
    <div>
      <div className="mb-8">
        <h1 className="font-display text-3xl font-extrabold tracking-wide mb-1">Dự đoán AI</h1>
        <p className="text-sm text-text2">
          ML model (LightGBM + FIFA Points) · {upcoming.length} trận sắp diễn ra
        </p>
      </div>

      {upcoming.length === 0 && (
        <p className="text-center text-text2 py-20 text-sm">Không có trận sắp diễn ra.</p>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {upcoming.map(m => <MatchCard key={m.id} match={m} prediction={predMap[m.id]} />)}
      </div>

      {/* Disclaimer */}
      <div className="mt-10 rounded-card border border-border bg-surface p-5 text-sm text-text2">
        <p className="font-semibold text-text mb-1">Về độ chính xác</p>
        <p>
          Model MVP đạt ~55–58% accuracy. Ngay cả betting companies chuyên nghiệp chỉ đạt ~65% —
          bóng đá có tính ngẫu nhiên cao. Đây là công cụ tham khảo, không phải lời khuyên cá cược.
        </p>
      </div>
    </div>
  )
}
