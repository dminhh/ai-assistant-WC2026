// src/lib/types.ts
export interface Match {
  id: number
  competition_id: number
  home_team: string
  away_team: string
  kickoff_time: string        // ISO UTC string
  status: "upcoming" | "live" | "finished"
  home_score: number | null
  away_score: number | null
  minute: number | null
}

export interface Competition {
  id: number
  name: string
  api_competition_id: string
  is_active: boolean
  competition_type: "national" | "club_europe"
  country: string | null
  season: string | null
  logo_url: string | null
}

export interface ScoreProb {
  score: string
  prob: number  // percentage e.g. 24.5
}

export interface Prediction {
  id: number
  match_id: number
  home_win_prob: number       // 0.0 – 1.0
  draw_prob: number
  away_win_prob: number
  predicted_score: string | null
  score_probs: ScoreProb[] | null
  confidence: "low" | "medium" | "high"
  model_version: string
  created_at: string
}

export interface StandingEntry {
  position: number
  team: { name: string; crest?: string }
  playedGames: number
  won: number
  draw: number
  lost: number
  goalDifference: number
  form: string | null         // e.g. "W,D,W,L,W"
  points: number
}

export interface TickerItem {
  text: string
  highlight?: string          // highlighted team/player name
}

export interface ChatMessage {
  role: "user" | "assistant"
  content: string
  isStreaming?: boolean
}
