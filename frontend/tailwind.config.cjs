/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: "var(--color-bg)",
        panel: "var(--color-panel)",
        panelSoft: "var(--color-panel-soft)",
        text: "var(--color-text)",
        textMuted: "var(--color-text-muted)",
        accent: "var(--color-accent)",
        accentAlt: "var(--color-accent-alt)",
        border: "var(--color-border)",
      },
      boxShadow: {
        panel: "0 10px 40px rgba(0,0,0,0.16)",
      },
      backgroundImage: {
        grid: "radial-gradient(circle at 1px 1px, rgba(148,163,184,0.15) 1px, transparent 0)",
      },
      backgroundSize: {
        grid: "20px 20px",
      },
    },
  },
  plugins: [],
};
