/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      colors: {
        // VidNotes palette: deep navy + electric violet + warm white
        canvas: '#0A0B14',
        surface: '#111320',
        border: '#1E2235',
        muted: '#2A2F4A',
        accent: '#7C6FFF',
        'accent-bright': '#9B8FFF',
        'accent-dim': '#3D3680',
        positive: '#34D399',
        warning: '#FBBF24',
        danger: '#F87171',
        'text-primary': '#F0F2FF',
        'text-secondary': '#8B90B8',
        'text-muted': '#4A5080',
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'slide-up': 'slideUp 0.3s ease-out',
        'fade-in': 'fadeIn 0.4s ease-out',
      },
      keyframes: {
        slideUp: {
          from: { transform: 'translateY(8px)', opacity: '0' },
          to: { transform: 'translateY(0)', opacity: '1' },
        },
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
}
