/** @type {import('tailwindcss').Config} */
module.exports = {
  // corePlugins:{
  //   preflight:false, 
  // }, 
  darkMode:'class',
  content: ["./core/**/*.{html,js}", "./authentication/**/*.{html,js}"],
  theme: {
    extend: {
      colors: {
        dark1: "#0F172A", 
        dark2: "#1E293B"
      }
    },
  },
  plugins: [],
}


/*
npx tailwindcss -i ./core/static/css/input.css -o ./core/static/css/output.css --watch
*/