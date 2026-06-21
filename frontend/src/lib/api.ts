// src/lib/api.ts
import type { Match, Competition, Prediction, StandingEntry } from "./types"

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

async function get<T>(path: string, revalidate = 30): Promise<T> {
  const isServer = typeof window === "undefined"
  const res = await fetch(`${BASE}${path}`, {
    ...(isServer ? { next: { revalidate } } : { cache: "no-store" }),
    headers: { "Content-Type": "application/json" },
  })
  if (!res.ok) throw new Error(`API ${res.status}: ${path}`)
  return res.json()
}

export const api = {
  getTodayMatches: () =>
    get<Match[]>("/matches/today", 60),

  getUpcomingMatches: (days = 14) =>
    get<Match[]>(`/matches/upcoming?days=${days}`, 300),

  getCompetitions: () =>
    get<Competition[]>("/competitions", 30),

  getPrediction: (matchId: number) =>
    get<Prediction>(`/predictions/${matchId}`, 300),

  getStandings: (competitionId: string) =>
    get<{ table: StandingEntry[] }[]>(`/standings/${competitionId}`, 120)
      .then(data => data.map(s => s.table)),

  /** Stream chat response via SSE. Returns cancel function. */
  streamChat: (
    message: string,
    onToken: (token: string) => void,
    onDone: () => void,
  ): (() => void) => {
    const ctrl = new AbortController()

    fetch(`${BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
      signal: ctrl.signal,
    }).then(async (res) => {
      const reader = res.body!.getReader()
      const decoder = new TextDecoder()
      let doneCalled = false
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const text = decoder.decode(value, { stream: true })
        for (const line of text.split("\n")) {
          if (!line.startsWith("data: ")) continue
          const payload = line.slice(6).trimEnd()
          if (payload === "[DONE]") { doneCalled = true; onDone(); return }
          onToken(payload)
        }
      }
      if (!doneCalled) onDone()
    }).catch(() => {})

    return () => ctrl.abort()
  },
}
