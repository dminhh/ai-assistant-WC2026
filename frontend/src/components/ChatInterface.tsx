"use client"
import { useState, useRef, useEffect, useCallback } from "react"
import { api } from "@/lib/api"
import type { ChatMessage } from "@/lib/types"

const SUGGESTIONS = [
  "Hôm nay có trận nào?",
  "Brazil vs France ai sẽ thắng?",
  "Ai đang dẫn đầu danh sách ghi bàn?",
  "Bảng G đội nào đứng đầu?",
  "Đội nào có khả năng vô địch WC2026 nhất?",
]

export function ChatInterface() {
  const [messages,    setMessages]    = useState<ChatMessage[]>([])
  const [input,       setInput]       = useState("")
  const [isStreaming, setIsStreaming] = useState(false)
  const cancelRef  = useRef<(() => void) | null>(null)
  const bottomRef  = useRef<HTMLDivElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  const sendMessage = useCallback((text: string) => {
    if (!text.trim() || isStreaming) return

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
          updated[updated.length - 1] = {
            ...last,
            content: last.content + token,
          }
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
    <div className="flex gap-5 h-[calc(100vh-12rem)]">
      {/* Chat window */}
      <div className="flex-1 flex flex-col bg-surface border border-border rounded-card overflow-hidden">
        {/* Header */}
        <div className="flex items-center gap-3 px-5 py-3.5 border-b border-border">
          <div className="w-7 h-7 rounded-full bg-amber/10 border border-amber/20 flex items-center justify-center text-sm">
            ⚽
          </div>
          <div>
            <p className="text-[13px] font-semibold text-text">AI Assistant</p>
            <p className="text-[11px] text-text3">GPT-4o · Dữ liệu thực tế</p>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
          {messages.length === 0 && (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center space-y-2">
                <p className="text-4xl">⚽</p>
                <p className="text-text2 text-sm">Hỏi bất kỳ điều gì về World Cup 2026</p>
              </div>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} className={`flex gap-2 max-w-[85%] ${msg.role === "user" ? "self-end flex-row-reverse" : "self-start"}`}>
              {msg.role === "assistant" && (
                <div className="w-6 h-6 rounded-full bg-amber/10 border border-amber/20 flex items-center justify-center text-[10px] text-amber flex-shrink-0 mt-1">
                  AI
                </div>
              )}
              <div>
                <div className={`px-3.5 py-2 rounded-2xl text-[13px] leading-relaxed ${
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
        <div className="flex gap-2 p-3 border-t border-border">
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === "Enter" && !e.shiftKey && sendMessage(input)}
            placeholder="Hỏi về World Cup 2026..."
            disabled={isStreaming}
            className="flex-1 bg-base border border-border rounded-lg px-3.5 py-2 text-[13px] text-text placeholder:text-text3 outline-none focus:border-amber/40 transition-colors disabled:opacity-50"
          />
          <button
            onClick={() => sendMessage(input)}
            disabled={isStreaming || !input.trim()}
            className="bg-amber text-base text-[13px] font-semibold rounded-lg px-4 transition-opacity hover:opacity-85 disabled:opacity-40"
          >
            →
          </button>
        </div>
      </div>

      {/* Sidebar */}
      <div className="w-[240px] flex-shrink-0 space-y-3">
        <div className="bg-surface border border-border rounded-card p-4">
          <p className="text-[10px] font-semibold tracking-[.1em] text-text3 uppercase mb-3">Gợi ý câu hỏi</p>
          <div className="space-y-2">
            {SUGGESTIONS.map(s => (
              <button
                key={s}
                onClick={() => sendMessage(s)}
                disabled={isStreaming}
                className="w-full text-left bg-none border border-border rounded-lg px-3 py-2 text-[12px] text-text2 transition-all hover:border-amber/30 hover:text-text disabled:opacity-40"
              >
                {s}
              </button>
            ))}
          </div>
        </div>

        <div className="bg-surface border border-border rounded-card p-4 text-[11px] text-text3 space-y-2">
          <p className="font-semibold text-text2">Về AI agents</p>
          <p><span className="text-green">⚡ ReAct</span> — câu hỏi data nhanh</p>
          <p><span className="text-amber">🔍 Reflection</span> — phân tích sâu & dự đoán</p>
        </div>
      </div>
    </div>
  )
}
