/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ferrari: {
          red: '#DC143C',
          darkred: '#B91C1C',
          black: '#000000',
          white: '#FFFFFF',
          yellow: '#FFFF00',
          gold: '#FFD700',
          silver: '#C0C0C0',
          blue: '#4A90E2',
          gray: {
            50: '#F9FAFB',
            100: '#F3F4F6',
            200: '#E5E7EB',
            300: '#D1D5DB',
            400: '#9CA3AF',
            500: '#6B7280',
            600: '#4B5563',
            700: '#374151',
            800: '#1F2937',
            900: '#111827',
          }
        }
      },
      fontFamily: {
        'mono': ['Monaco', 'Menlo', 'Ubuntu Mono', 'monospace'],
        'racing': ['Rajdhani', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'bounce-slow': 'bounce 2s infinite',
        'flash': 'flash 1s ease-in-out infinite alternate',
      },
      keyframes: {
        flash: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0.5' },
        },
      },
      backdropBlur: {
        xs: '2px',
      },
    },
  },
  plugins: [],
} 