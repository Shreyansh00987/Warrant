import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        paper: {
          DEFAULT: "#F6F1E7",
          light: "#FAF7F0",
          dark: "#EDE6D6",
          card: "#FAF6EE",
        },
        ink: {
          DEFAULT: "#1A1A1A",
          muted: "#5B5648",
          faint: "#8C8677",
        },
        rule: {
          DEFAULT: "#D9D0BE",
          light: "#EAE3D4",
          dark: "#C5BBA4",
        },
        oxblood: {
          DEFAULT: "#8B1E2D",
          light: "#A4283A",
          dark: "#6B1421",
          faint: "#F6EAEB",
        },
        verified: {
          DEFAULT: "#2F6B3B",
          light: "#3A8549",
          faint: "#EAF2EC",
        },
      },
      fontFamily: {
        serif: ["Newsreader", "Fraunces", "Georgia", "serif"],
        sans: ["Inter", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "sans-serif"],
        mono: ["JetBrains Mono", "SFMono-Regular", "Menlo", "Consolas", "monospace"],
      },
      boxShadow: {
        warrant: "0 4px 20px -2px rgba(26, 26, 26, 0.08), 0 1px 3px 0 rgba(26, 26, 26, 0.04)",
      },
      keyframes: {
        "stamp-press": {
          "0%": { transform: "scale(1.3) rotate(-6deg)", opacity: "0" },
          "60%": { transform: "scale(0.97) rotate(-1.5deg)", opacity: "0.95" },
          "100%": { transform: "scale(1) rotate(-2deg)", opacity: "1" },
        },
        "stamp-press-red": {
          "0%": { transform: "scale(1.3) rotate(5deg)", opacity: "0" },
          "60%": { transform: "scale(0.97) rotate(1.5deg)", opacity: "0.95" },
          "100%": { transform: "scale(1) rotate(2deg)", opacity: "1" },
        },
        "pulse-subtle": {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.4" },
        },
      },
      animation: {
        stamp: "stamp-press 0.28s cubic-bezier(0.16, 1, 0.3, 1) forwards",
        "stamp-red": "stamp-press-red 0.28s cubic-bezier(0.16, 1, 0.3, 1) forwards",
        "pulse-subtle": "pulse-subtle 2s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
