"use client"
import { useState } from "react"
import { useRouter } from "next/navigation"
import { login } from "@/lib/auth"

export default function LoginPage() {
  const router = useRouter()
  const [email,    setEmail]    = useState("")
  const [password, setPassword] = useState("")
  const [error,    setError]    = useState("")
  const [loading,  setLoading]  = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError("")
    setLoading(true)
    try {
      await login(email, password)
      router.push("/admin")
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Đăng nhập thất bại")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-[70vh] flex items-center justify-center">
      <div className="w-full max-w-sm bg-surface border border-border rounded-card p-8">
        <h1 className="font-display text-2xl font-extrabold tracking-wide mb-1">Đăng nhập</h1>
        <p className="text-sm text-text2 mb-7">Admin · WC2026</p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-[11px] font-semibold tracking-widest text-text3 uppercase">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
              className="w-full bg-base border border-border rounded-lg px-3.5 py-2.5 text-sm text-text placeholder:text-text3 outline-none focus:border-amber/40 transition-colors"
              placeholder="admin@example.com"
            />
          </div>

          <div className="space-y-1.5">
            <label className="text-[11px] font-semibold tracking-widest text-text3 uppercase">
              Mật khẩu
            </label>
            <input
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
              className="w-full bg-base border border-border rounded-lg px-3.5 py-2.5 text-sm text-text placeholder:text-text3 outline-none focus:border-amber/40 transition-colors"
              placeholder="••••••••"
            />
          </div>

          {error && (
            <p className="text-sm text-red bg-red/10 border border-red/20 rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-amber text-base font-semibold rounded-lg py-2.5 text-sm transition-opacity hover:opacity-85 disabled:opacity-50 mt-2"
          >
            {loading ? "Đang đăng nhập..." : "Đăng nhập"}
          </button>
        </form>
      </div>
    </div>
  )
}
