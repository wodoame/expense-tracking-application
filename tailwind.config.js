/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode:'class',
  content: ["./core/**/*.{html,js}", "./authentication/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        dark1: "#0F172A", 
        dark2: "#1E293B", 
        darkborder:"rgb(243 244 246 / 0.05)"
      }
    },
  },
  plugins: [],
}


/*
npx tailwindcss -i ./core/static/css/input.css -o ./core/static/css/output.css --watch
*/