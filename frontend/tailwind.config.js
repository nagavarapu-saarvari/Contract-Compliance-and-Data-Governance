/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: "#eef6fa",
          100: "#dbeaf3",
          200: "#b7d6e7",
          300: "#8fc0d8",
          400: "#1e648f",
          500: "#1a587d",
          600: "#164c6b",
          700: "#124059",
          800: "#0e3447",
          900: "#0a2835",
        },
      },
    },
  },
  plugins: [],
};