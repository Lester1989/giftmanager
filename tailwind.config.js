/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./app/templates/*.html"],
  theme: {
    colors: {
      transparent: "transparent",
      current: "currentColor",
      black: "#000",
      white: "#fff",
      blue: {
        200: "#E6F0F5",
        400: "#B3D1E0",
        600: "#80B2CC",	// Main Blue color */
        800: "#4D93B8",
        1000: "#2665A3"
      },
      gray:{
        100: "#F5F5F5",
        200: "#EEEEEE",
        300: "#E0E0E0",
        400: "#BDBDBD",
        500: "#9E9E9E",  // Main Gray color */
        600: "#757575",
        700: "#616161",
        800: "#424242",
        900: "#212121",
        1000: "#101010"
      },
      slate:{
        100: "#ECEFF1",
        300: "#CFD8DC",
        500: "#B0BEC5",	// Main Slate color */
        700: "#90A4AE",
        900: "#607D8B"
      },
      primary:{
        100: "#6F7DA3",
        300: "#465785",
        500: "#2B3D6C",	// Main Primary color */
        700: "#152551",
        900: "#061235"
      },
      secondary:{
        100: "#7F71A6",
        300: "#594888",
        500: "#3E2C6F",	// Main Secondary color (1) */
        700: "#251552",
        900: "#130636"
      },
      tertiary:{
        100: "#5F8F93",
        300: "#3A7378",
        500: "#215C62",	// Main Secondary color (2) */
        700: "#0D4449",
        900: "#012C30"
      }
    },
    extend: {},
  },
  plugins: [],
}

