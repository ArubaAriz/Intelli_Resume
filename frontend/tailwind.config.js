export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#0F1117",
        "ink-light": "#1C202B",
        "ink-mid": "#252A38",
        border: "#2E3447",
        accent: "#6366F1",
        "accent-light": "#818CF8",
        "accent-glow": "#4F52D9",
        success: "#10B981",
        warning: "#F59E0B",
        danger: "#EF4444",
        muted: "#64748B",
        "text-primary": "#F1F5F9",
        "text-secondary": "#94A3B8",
      },
      fontFamily: {
        display: ["'Plus Jakarta Sans'", "sans-serif"],
        body: ["'Inter'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
    },
  },
  plugins: [],
}
