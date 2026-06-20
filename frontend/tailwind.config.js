/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        wfrp: {
          bg: "#0D0B08",
          surface: "#1A1612",
          raised: "#241E17",
          fg: "#E8DCC8",
          muted: "#9E8E72",
          "muted-dim": "#5C5040",
          border: "#2E2820",
          accent: "#C9973A",
          success: "#3A5C2E",
          danger: "#8B1A1A",
          combat: "#1E2D4A",
          highlight: "#F0E6D0",
        },
      },
      fontFamily: {
        display: ["var(--font-cinzel)", "Georgia", "serif"],
        narrative: ["var(--font-crimson)", "Georgia", "serif"],
        ui: ["var(--font-source)", "system-ui", "sans-serif"],
        mono: ["ui-monospace", "Menlo", "monospace"],
      },
      maxWidth: {
        container: "1120px",
      },
    },
  },
  plugins: [],
};
