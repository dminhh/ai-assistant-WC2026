import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base:     "#050810",
        surface:  "#0C1220",
        surface2: "#111A2E",
        border:   "#1A2640",
        gold:     "#FFD700",
        gold2:    "#C9A227",
        amber:    "#FFD700",
        green:    "#2DC653",
        blue:     "#4895EF",
        slate:    "#4A6080",
        red:      "#E63946",
        text:     "#F0EDE4",
        text2:    "#7A8FA8",
        text3:    "#3A4F66",
      },
      fontFamily: {
        display: ["'Barlow Condensed'", "sans-serif"],
        body:    ["Inter", "sans-serif"],
        mono:    ["'JetBrains Mono'", "monospace"],
      },
      borderRadius: {
        card: "14px",
        pill: "999px",
      },
      boxShadow: {
        gold:  "0 0 20px rgba(255,215,0,0.12), 0 0 40px rgba(255,215,0,0.05)",
        "gold-sm": "0 0 10px rgba(255,215,0,0.15)",
        red:   "0 0 24px rgba(230,57,70,0.20), 0 0 48px rgba(230,57,70,0.08)",
        card:  "0 4px 24px rgba(0,0,0,0.4)",
      },
    },
  },
  plugins: [],
}
export default config
