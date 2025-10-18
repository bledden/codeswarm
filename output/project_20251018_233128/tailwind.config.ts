import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/app/**/*.{js,ts,jsx,tsx}",
    "./src/components/**/*.{js,ts,jsx,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: "var(--color-brand)",
          dark: "var(--color-brand-dark)",
          light: "var(--color-brand-light)"
        },
        ink: {
          DEFAULT: "var(--color-ink)",
          light: "var(--color-ink-light)",
          faded: "var(--color-ink-faded)"
        },
        bg: {
          DEFAULT: "var(--color-bg)",
          subtle: "var(--color-bg-subtle)"
        },
        success: "var(--color-success)",
        error: "var(--color-error)",
        warning: "var(--color-warning)"
      },
      spacing: {
        "xs": "var(--space-xs)",
        "sm": "var(--space-sm)",
        "md": "var(--space-md)",
        "lg": "var(--space-lg)",
        "xl": "var(--space-xl)",
        "2xl": "var(--space-2xl)"
      },
      boxShadow: {
        card: "0 8px 30px rgba(0, 0, 0, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;