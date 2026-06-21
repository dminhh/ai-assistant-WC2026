"use client"
import { useState, useRef, useEffect, useCallback } from "react"
import { api } from "@/lib/api"
import type { ChatMessage } from "@/lib/types"
import { BotAvatar } from "./BotAvatar"

const SUGGESTIONS = [
  "Hôm nay có trận nào?",
  "Brazil vs France ai sẽ thắng?",
  "Bảng G đội nào đứng đầu?",
  "Đội nào có khả năng vô địch WC2026 nhất?",
]

export function ChatInterface() {
  const [messages,    setMessages]    = useState<ChatMessage[]>([])
  const [input,       setInput]       = useState("")
  const [isStreaming, setIsStreaming] = useState(false)
  const [showSidebar, setShowSidebar] = useState(false)
  const cancelRef  = useRef<(() => void) | null>(null)
  const bottomRef  = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = useCallback((text: string) => {
    if (!text.trim() || isStreaming) return
    setShowSidebar(false)
    const userMsg: ChatMessage      = { role: "user", content: text }
    const assistantMsg: ChatMessage = { role: "assistant", content: "", isStreaming: true }
    setMessages(prev => [...prev, userMsg, assistantMsg])
    setInput("")
    setIsStreaming(true)

    cancelRef.current = api.streamChat(
      text,
      (token) => {
        setMessages(prev => {
          const updated = [...prev]
          const last    = updated[updated.length - 1]
          updated[updated.length - 1] = { ...last, content: last.content + token }
          return updated
        })
      },
      () => {
        setIsStreaming(false)
        setMessages(prev => {
          const updated = [...prev]
          updated[updated.length - 1] = { ...updated[updated.length - 1], isStreaming: false }
          return updated
        })
      },
    )
  }, [isStreaming])

  return (
    <div className="flex flex-col md:flex-row gap-4 md:gap-5 h-[calc(100vh-10rem)] md:h-[calc(100vh-12rem)]">
      {/* Chat window */}
      <div className="flex-1 flex flex-col rounded-card overflow-hidden min-h-0"
        style={{ background: "linear-gradient(145deg, #0C1220, #0a1028)", border: "1px solid #1A2640" }}
      >
        {/* Header */}
        <div className="flex items-center gap-3 px-4 md:px-5 py-3 border-b border-border flex-shrink-0">
          <BotAvatar size={32} isTyping={isStreaming} />
          <div className="flex-1 min-w-0">
            <p className="text-[13px] font-semibold text-text">AI Assistant</p>
            <p className="text-[11px] text-text3 truncate">{isStreaming ? "Đang trả lời..." : "GPT-4o · Dữ liệu thực tế"}</p>
          </div>
          {/* Mobile suggestions toggle */}
          <button
            className="md:hidden text-text3 hover:text-text2 text-xs px-2 py-1 border border-border rounded-lg"
            onClick={() => setShowSidebar(v => !v)}
          >
            Gợi ý
          </button>
        </div>

        {/* Mobile suggestions dropdown */}
        {showSidebar && (
          <div className="md:hidden flex flex-wrap gap-2 px-4 py-3 border-b border-border flex-shrink-0">
            {SUGGESTIONS.map(s => (
              <button key={s} onClick={() => sendMessage(s)} disabled={isStreaming}
                className="text-[11px] text-text2 border border-border rounded-lg px-2.5 py-1.5 hover:border-gold/30 hover:text-text disabled:opacity-40 transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-3 md:p-4 flex flex-col gap-3 md:gap-4">
          {messages.length === 0 && (
            <div className="flex gap-2 self-start max-w-[90%] md:max-w-[85%]">
              <BotAvatar size={24} />
              <div className="px-3 py-2.5 rounded-2xl rounded-bl-sm text-[13px] leading-relaxed bg-surface2 text-text space-y-1">
                <p>Xin chào công túa! 👋</p>
                <p className="text-text2 text-[12px]">Thần là AI chuyên về World Cup 2026. Công túa có thể hỏi về lịch thi đấu, kết quả, bảng xếp hạng, dự đoán tỉ số hay thống kê các đội bóng nhé!</p>
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-2 max-w-[90%] md:max-w-[85%] ${msg.role === "user" ? "self-end flex-row-reverse" : "self-start"}`}>
              {msg.role === "assistant" && <BotAvatar size={24} isTyping={!!msg.isStreaming} />}
              <div>
                <div className={`px-3 py-2.5 rounded-2xl text-[13px] leading-relaxed ${
                  msg.role === "user"
                    ? "bg-amber text-base font-medium rounded-br-sm"
                    : "bg-surface2 text-text rounded-bl-sm"
                }`}>
                  {msg.content || (
                    msg.isStreaming
                      ? <span className="flex gap-1 py-0.5">
                          {[0, 150, 300].map(d => (
                            <span key={d} className="w-1.5 h-1.5 rounded-full bg-text3 animate-bounce" style={{ animationDelay: `${d}ms` }} />
                          ))}
                        </span>
                      : null
                  )}
                  {msg.isStreaming && msg.content && (
                    <span className="inline-block w-0.5 h-3.5 bg-amber ml-0.5 align-middle animate-pulse" />
                  )}
                </div>
              </div>
            </div>
          ))}
          <div ref={bottomRef} />
        </div>

        {/* Input */}
        <div className="flex gap-2 p-3 border-t border-border flex-shrink-0">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !e.shiftKey && sendMessage(input)}
            placeholder="Hỏi về World Cup 2026..."
            disabled={isStreaming}
            className="flex-1 bg-base border border-border rounded-lg px-3 py-2 text-[13px] text-text placeholder:text-text3 outline-none focus:border-amber/40 transition-colors disabled:opacity-50"
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={isStreaming || !input.trim()}
            className="bg-amber text-base text-[13px] font-semibold rounded-lg px-3 md:px-4 transition-opacity hover:opacity-85 disabled:opacity-40 flex-shrink-0"
          >
            →
          </button>
        </div>
      </div>

      {/* Desktop Sidebar */}
      <div className="hidden md:flex w-[220px] flex-shrink-0 flex-col gap-3">
        <div className="rounded-card p-4" style={{ background: "linear-gradient(145deg, #0C1220, #0a1028)", border: "1px solid #1A2640" }}>
          <p className="text-[10px] font-semibold tracking-[.1em] text-text3 uppercase mb-3">Gợi ý câu hỏi</p>
          <div className="space-y-2">
            {SUGGESTIONS.map(s => (
              <button key={s} onClick={() => sendMessage(s)} disabled={isStreaming}
                className="w-full text-left border border-border rounded-lg px-3 py-2 text-[12px] text-text2 transition-all hover:border-gold/30 hover:text-text disabled:opacity-40"
                style={{ background: "transparent" }}
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className="rounded-card p-4 text-[11px] text-text3 space-y-2" style={{ background: "linear-gradient(145deg, #0C1220, #0a1028)", border: "1px solid #1A2640" }}>
          <p className="font-semibold text-text2">Về AI agents</p>
          <p><span className="text-green">⚡ ReAct</span> — câu hỏi data nhanh</p>
          <p><span className="text-amber">🔍 Reflection</span> — phân tích sâu & dự đoán</p>
        </div>
      </div>
    </div>
  )
}
