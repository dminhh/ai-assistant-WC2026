import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        base:     "#0A0E1A",
        surface:  "#0F1829",
        surface2: "#162035",
        border:   "#1E2A3A",
        amber:    "#F5A623",
        green:    "#2D9E6B",
        blue:     "#3B82F6",
        slate:    "#64748B",
        red:      "#EF4444",
        text:     "#F0EDE4",
        text2:    "#8A9BB5",
        text3:    "#4A5A6E",
      },
      fontFamily: {
        display: ["'Barlow Condensed'", "sans-serif"],
        body:    ["Inter", "sans-serif"],
        mono:    ["'JetBrains Mono'", "monospace"],
      },
      borderRadius: {
        card: "10px",
        pill: "999px",
      },
    },
  },
  plugins: [],
}
export default config
