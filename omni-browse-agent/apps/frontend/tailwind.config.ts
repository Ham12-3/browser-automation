import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#151515",
        muted: "#5f6673",
        line: "#d8dde6",
        paper: "#f6f7f9",
        panel: "#ffffff",
        mint: "#dff5ea",
        blue: "#dfeafd",
        amber: "#fff0cc",
        rust: "#b64b3a"
      }
    }
  },
  plugins: []
};

export default config;
