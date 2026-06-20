import { ChatInterface } from "@/components/ChatInterface"

export default function ChatPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="font-display text-3xl font-extrabold tracking-wide mb-1">AI Chat</h1>
        <p className="text-sm text-text2">Hỏi về lịch thi đấu, dự đoán, thống kê World Cup 2026</p>
      </div>
      <ChatInterface />
    </div>
  )
}
