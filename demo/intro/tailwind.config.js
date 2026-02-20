/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: [
          '-apple-system', 'BlinkMacSystemFont', '"Segoe UI"', 'Roboto',
          'Helvetica', 'Arial', 'sans-serif',
        ],
        mono: [
          'Menlo', 'Monaco', 'Consolas', '"Liberation Mono"',
          '"Courier New"', 'monospace',
        ],
      },
      colors: {
        accent: '#FF6600',
      },
    },
  },
  plugins: [],
};
