/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Figtree"', '"Cairo"', "sans-serif"],
        sans: ['"Figtree"', '"Cairo"', "sans-serif"],
      },
      colors: {
        ink: {
          DEFAULT: "#000000",
          soft: "#242424",
          muted: "#666666",
        },
        paper: {
          DEFAULT: "#F4F0E8",
          raised: "#FBFAF7",
          line: "#CFC7BA",
        },
        signal: {
          DEFAULT: "#000000",
          soft: "#F2F2F2",
        },
        verify: {
          DEFAULT: "#000000",
          soft: "#F2F2F2",
        },
      },
      boxShadow: {
        panel: "0 1px 0 rgba(0, 0, 0, 0.06)",
      },
    },
  },
  plugins: [],
};
