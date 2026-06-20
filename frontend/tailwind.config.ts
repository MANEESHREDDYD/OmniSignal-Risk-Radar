import type { Config } from "tailwindcss";

export default {
  content: ["./app/**/*.{js,ts,jsx,tsx,mdx}", "./components/**/*.{js,ts,jsx,tsx,mdx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17212B",
        paper: "#F4F2ED",
        signal: "#E64B3C",
        amber: "#E79A34",
        moss: "#45836A",
      },
      boxShadow: {
        card: "0 18px 50px rgba(25, 34, 42, 0.08)",
      },
    },
  },
  plugins: [],
} satisfies Config;

