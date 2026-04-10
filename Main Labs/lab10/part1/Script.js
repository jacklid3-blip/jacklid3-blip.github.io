// setup canvas

const canvas = document.querySelector("canvas"); // Get canvas element
const ctx = canvas.getContext("2d");             // Get 2D drawing context

const width = (canvas.width = window.innerWidth);   // Set canvas width to window width
const height = (canvas.height = window.innerHeight); // Set canvas height to window height

// function to generate random number

function random(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min; // Return random int between min and max
}

// function to generate random color

function randomRGB() {
  return `rgb(${random(0, 255)},${random(0, 255)},${random(0, 255)})`; // Return random RGB color string
}