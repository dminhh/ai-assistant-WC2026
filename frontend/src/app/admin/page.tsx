"use client"
import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { isLoggedIn, clearToken, authHeaders } from "@/lib/auth"
import type { Competition } from "@/lib/types"

const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"

export default function AdminPage() {
  const router = useRouter()
  const [competitions, setCompetitions] = useState<Competition[]>([])
  const [syncing,  setSyncing]  = useState(false)
  const [syncMsg,  setSyncMsg]  = useState("")
  const [adding,   setAdding]   = useState(false)
  const [form, setForm] = useState({
    name: "", api_competition_id: "", competition_type: "national",
    country: "", season: "", is_active: true,
  })

  const fetchCompetitions = useCallback(async () => {
    const res = await fetch(`${BASE}/competitions`)
    if (res.ok) setCompetitions(await res.json())
  }, [])

  useEffect(() => {
    if (!isLoggedIn()) { router.push("/login"); return }
    fetchCompetitions()
  }, [router, fetchCompetitions])

  async function handleToggle(id: number) {
    await fetch(`${BASE}/competitions/${id}/toggle`, {
      method: "PATCH",
      headers: authHeaders(),
    })
    fetchCompetitions()
  }

  async function handleSync() {
    setSyncing(true)
    setSyncMsg("")
    try {
      const res = await fetch(`${BASE}/admin/sync`, {
        method: "POST",
        headers: authHeaders(),
      })
      const data = await res.json()
      setSyncMsg(`Đã sync: ${data.synced.join(", ") || "Không có giải nào active"}`)
    } catch {
      setSyncMsg("Sync thất bại")
    } finally {
      setSyncing(false)
    }
  }

  async function handleAddCompetition(e: React.FormEvent) {
    e.preventDefault()
    const res = await fetch(`${BASE}/competitions`, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify({
        ...form,
        country: form.country || null,
        season: form.season || null,
      }),
    })
    if (res.ok) {
      setAdding(false)
      setForm({ name: "", api_competition_id: "", competition_type: "national", country: "", season: "", is_active: true })
      fetchCompetitions()
    }
  }

  function handleLogout() {
    clearToken()
    router.push("/login")
  }

  const COMP_TYPE_LABEL: Record<string, string> = { national: "ĐTQG", club_europe: "CLB" }

  return (
    <div className="max-w-2xl">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="font-display text-3xl font-extrabold tracking-wide mb-1">Admin</h1>
          <p className="text-sm text-text2">Quản lý giải đấu · WC2026</p>
        </div>
        <button
          onClick={handleLogout}
          className="text-[12px] text-text3 border border-border rounded-lg px-3 py-1.5 hover:border-red/40 hover:text-red transition-colors"
        >
          Đăng xuất
        </button>
      </div>

      {/* Sync section */}
      <div className="bg-surface border border-border rounded-card p-5 mb-6">
        <div className="flex items-center justify-between mb-2">
          <p className="text-sm font-semibold text-text">Đồng bộ dữ liệu</p>
          <button
            onClick={handleSync}
            disabled={syncing}
            className="bg-amber text-base text-[12px] font-semibold rounded-lg px-4 py-1.5 transition-opacity hover:opacity-85 disabled:opacity-50"
          >
            {syncing ? "Đang sync..." : "⚡ Sync ngay"}
          </button>
        </div>
        <p className="text-[12px] text-text3">
          Fetch matches từ football-data.org cho tất cả giải đang active.
        </p>
        {syncMsg && (
          <p className="mt-2 text-[12px] text-green">{syncMsg}</p>
        )}
      </div>

      {/* Competitions list */}
      <div className="bg-surface border border-border rounded-card overflow-hidden mb-4">
        <div className="flex items-center justify-between px-5 py-4 border-b border-border">
          <p className="text-sm font-semibold text-text">Giải đấu ({competitions.length})</p>
          <button
            onClick={() => setAdding(v => !v)}
            className="text-[12px] text-amber border border-amber/30 rounded-lg px-3 py-1 hover:bg-amber/10 transition-colors"
          >
            + Thêm giải
          </button>
        </div>

        {competitions.length === 0 && (
          <p className="text-sm text-text3 text-center py-8">Chưa có giải nào. Thêm giải bên dưới.</p>
        )}

        {competitions.map(comp => (
          <div key={comp.id} className="flex items-center justify-between px-5 py-3.5 border-b border-border last:border-0">
            <div>
              <p className="text-sm font-medium text-text">{comp.name}</p>
              <p className="text-[11px] text-text3 mt-0.5">
                ID: {comp.api_competition_id} · {COMP_TYPE_LABEL[comp.competition_type] ?? comp.competition_type}
                {comp.season && ` · ${comp.season}`}
              </p>
            </div>
            <button
              onClick={() => handleToggle(comp.id)}
              className={`text-[11px] font-semibold px-3 py-1 rounded-pill border transition-colors ${
                comp.is_active
                  ? "text-green bg-green/10 border-green/20 hover:bg-green/20"
                  : "text-text3 bg-surface2 border-border hover:border-text3"
              }`}
            >
              {comp.is_active ? "Active" : "Inactive"}
            </button>
          </div>
        ))}
      </div>

      {/* Add competition form */}
      {adding && (
        <div className="bg-surface border border-border rounded-card p-5">
          <p className="text-sm font-semibold text-text mb-4">Thêm giải đấu mới</p>
          <form onSubmit={handleAddCompetition} className="space-y-3">
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1 col-span-2">
                <label className="text-[10px] font-semibold tracking-widest text-text3 uppercase">Tên giải</label>
                <input required value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                  className="w-full bg-base border border-border rounded-lg px-3 py-2 text-sm text-text outline-none focus:border-amber/40"
                  placeholder="FIFA World Cup 2026" />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-semibold tracking-widest text-text3 uppercase">API ID</label>
                <input required value={form.api_competition_id} onChange={e => setForm(f => ({ ...f, api_competition_id: e.target.value }))}
                  className="w-full bg-base border border-border rounded-lg px-3 py-2 text-sm text-text outline-none focus:border-amber/40"
                  placeholder="2000" />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-semibold tracking-widest text-text3 uppercase">Loại</label>
                <select value={form.competition_type} onChange={e => setForm(f => ({ ...f, competition_type: e.target.value }))}
                  className="w-full bg-base border border-border rounded-lg px-3 py-2 text-sm text-text outline-none focus:border-amber/40">
                  <option value="national">ĐTQG</option>
                  <option value="club_europe">CLB</option>
                </select>
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-semibold tracking-widest text-text3 uppercase">Quốc gia</label>
                <input value={form.country} onChange={e => setForm(f => ({ ...f, country: e.target.value }))}
                  className="w-full bg-base border border-border rounded-lg px-3 py-2 text-sm text-text outline-none focus:border-amber/40"
                  placeholder="England (tuỳ chọn)" />
              </div>
              <div className="space-y-1">
                <label className="text-[10px] font-semibold tracking-widest text-text3 uppercase">Mùa giải</label>
                <input value={form.season} onChange={e => setForm(f => ({ ...f, season: e.target.value }))}
                  className="w-full bg-base border border-border rounded-lg px-3 py-2 text-sm text-text outline-none focus:border-amber/40"
                  placeholder="2026 (tuỳ chọn)" />
              </div>
            </div>
            <div className="flex items-center gap-2 pt-1">
              <input type="checkbox" id="is_active" checked={form.is_active}
                onChange={e => setForm(f => ({ ...f, is_active: e.target.checked }))}
                className="accent-amber" />
              <label htmlFor="is_active" className="text-sm text-text2">Kích hoạt ngay</label>
            </div>
            <div className="flex gap-2 pt-2">
              <button type="submit"
                className="bg-amber text-base text-[12px] font-semibold rounded-lg px-4 py-2 hover:opacity-85 transition-opacity">
                Thêm giải
              </button>
              <button type="button" onClick={() => setAdding(false)}
                className="text-[12px] text-text3 border border-border rounded-lg px-4 py-2 hover:border-text3 transition-colors">
                Huỷ
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  )
}
