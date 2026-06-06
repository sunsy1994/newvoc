import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      boxShadow: {
        soft: "0 24px 80px rgba(24, 31, 42, 0.08)",
      },
    },
  },
  plugins: [],
};

export default config;
