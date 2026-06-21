"use client"

export function BotAvatar({ size = 28, isTyping = false }: { size?: number; isTyping?: boolean }) {
  return (
    <div className="relative flex-shrink-0" style={{ width: size, height: size }}>
      <svg
        width={size}
        height={size}
        viewBox="0 0 40 40"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Glow background */}
        <circle cx="20" cy="20" r="19" fill="url(#bgGrad)" />
        <circle cx="20" cy="20" r="19" stroke="rgba(255,215,0,0.3)" strokeWidth="1" />

        {/* Antenna */}
        <line x1="20" y1="5" x2="20" y2="11" stroke="rgba(255,215,0,0.7)" strokeWidth="1.5" strokeLinecap="round" />
        <circle cx="20" cy="4" r="1.8" fill="#FFD700">
          <animate attributeName="opacity" values="1;0.4;1" dur="1.8s" repeatCount="indefinite" />
        </circle>

        {/* Head */}
        <rect x="9" y="11" width="22" height="18" rx="5" fill="url(#headGrad)" />
        <rect x="9" y="11" width="22" height="18" rx="5" stroke="rgba(255,215,0,0.2)" strokeWidth="0.8" />

        {/* Eyes */}
        <circle cx="15.5" cy="19" r="3" fill="rgba(0,0,0,0.4)" />
        <circle cx="24.5" cy="19" r="3" fill="rgba(0,0,0,0.4)" />
        {/* Eye glow */}
        <circle cx="15.5" cy="19" r="2" fill="#4895EF">
          <animate attributeName="r" values="2;1.4;2" dur="2.4s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="1;0.6;1" dur="2.4s" repeatCount="indefinite" />
        </circle>
        <circle cx="24.5" cy="19" r="2" fill="#4895EF">
          <animate attributeName="r" values="2;1.4;2" dur="2.4s" begin="0.3s" repeatCount="indefinite" />
          <animate attributeName="opacity" values="1;0.6;1" dur="2.4s" begin="0.3s" repeatCount="indefinite" />
        </circle>
        {/* Eye shine */}
        <circle cx="16.5" cy="18" r="0.7" fill="white" opacity="0.8" />
        <circle cx="25.5" cy="18" r="0.7" fill="white" opacity="0.8" />

        {/* Mouth */}
        {isTyping ? (
          // Talking mouth animation
          <rect x="14" y="24" width="12" height="2.5" rx="1.2" fill="rgba(255,215,0,0.5)">
            <animate attributeName="height" values="2.5;4;2.5;1;2.5" dur="0.6s" repeatCount="indefinite" />
            <animate attributeName="y" values="24;23;24;24.5;24" dur="0.6s" repeatCount="indefinite" />
          </rect>
        ) : (
          <path d="M14 24.5 Q20 27.5 26 24.5" stroke="rgba(255,215,0,0.6)" strokeWidth="1.5" strokeLinecap="round" fill="none" />
        )}

        {/* Body */}
        <rect x="14" y="30" width="12" height="6" rx="3" fill="url(#bodyGrad)" />

        {/* Signal waves when typing */}
        {isTyping && (
          <>
            <circle cx="34" cy="14" r="1.5" fill="rgba(255,215,0,0.0)">
              <animate attributeName="r" values="1;5;1" dur="1.5s" repeatCount="indefinite" />
              <animate attributeName="opacity" values="0.6;0;0.6" dur="1.5s" repeatCount="indefinite" />
              <animate attributeName="fill" values="rgba(255,215,0,0.6);rgba(255,215,0,0)" dur="1.5s" repeatCount="indefinite" />
            </circle>
          </>
        )}

        <defs>
          <radialGradient id="bgGrad" cx="50%" cy="40%" r="55%">
            <stop offset="0%" stopColor="#0F1E38" />
            <stop offset="100%" stopColor="#050810" />
          </radialGradient>
          <linearGradient id="headGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#1A2E50" />
            <stop offset="100%" stopColor="#0D1828" />
          </linearGradient>
          <linearGradient id="bodyGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="rgba(255,215,0,0.3)" />
            <stop offset="100%" stopColor="rgba(255,215,0,0.1)" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  )
}
