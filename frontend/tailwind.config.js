/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#F0F9FC',
          100: '#DDF2F8',
          200: '#BFE7F5',
          300: '#7ECBE5',
          400: '#4FC3E0',
          500: '#1D7A9C',
          600: '#146482',
          700: '#0E4E67',
          800: '#0B3D5C',
          900: '#082C43',
        },
        coral: {
          DEFAULT: '#FF6B5A',
          hover: '#FA5845',
          light: '#FFF0EE',
        },
        palm: {
          DEFAULT: '#2F9E6B',
          light: '#E8F6EF',
        },
        gold: {
          DEFAULT: '#E8A33D',
          light: '#FDF6EB',
        },
        sand: {
          DEFAULT: '#FAF7F2',
          card: '#FFFFFF',
          dark: '#F0EBE1',
        },
        ink: {
          DEFAULT: '#0D2538',
          muted: '#557082',
          light: '#8FA4B2',
        }
      },
      fontFamily: {
        display: ['"Baloo 2"', 'sans-serif'],
        sans: ['Inter', 'sans-serif'],
      },
      boxShadow: {
        'glow': '0 0 25px -5px rgba(79, 195, 224, 0.4)',
        'card': '0 8px 30px rgba(11, 61, 92, 0.07)',
        'card-hover': '0 16px 40px rgba(11, 61, 92, 0.12)',
      },
      borderRadius: {
        'xl': '18px',
        '2xl': '24px',
        '3xl': '32px',
      }
    },
  },
  plugins: [],
}
