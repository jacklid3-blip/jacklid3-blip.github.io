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

class Ball {
  constructor(x, y, velX, velY, color, size) {
    this.x = x;
    this.y = y;
    this.velX = velX;
    this.velY = velY;
    this.color = color;
    this.size = size;
  }

  draw() {
    ctx.beginPath();
    ctx.fillStyle = this.color;
    ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);
    ctx.fill();
  }

  update() {
    if (this.x + this.size >= width || this.x - this.size <= 0) {
      this.velX = -this.velX;
    }

    if (this.y + this.size >= height || this.y - this.size <= 0) {
      this.velY = -this.velY;
    }

    this.x += this.velX;
    this.y += this.velY;
  }
}