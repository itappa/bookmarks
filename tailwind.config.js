/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/*.html",
    "./templates/**/*.html",
  ],
  theme: {
    extend: {
      screens: {
        "3xl": "1920px",
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}

