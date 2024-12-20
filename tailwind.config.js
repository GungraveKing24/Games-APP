/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./templates/**/*.html",  // Asegúrate de incluir tus archivos .html
    "./static/js/**/*.js",    // Si tienes archivos JS en la carpeta static
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}

