/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#F8F8F5',
        primary: '#A8D5BA',
        secondary: '#A9DEF9',
        accent1: '#CDB4DB',
        accent2: '#FFD6BA',
        accent3: '#B8F2E6',
        accent4: '#FFF3B0',
        text1: '#1F2937',
        text2: '#6B7280',
        border: '#E8E8E4',
      },
      fontFamily: {
        sans: ['DM Sans', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
