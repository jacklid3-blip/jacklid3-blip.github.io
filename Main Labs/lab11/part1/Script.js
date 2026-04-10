// set up canvas

const canvas = document.querySelector("canvas"); // Get canvas element
const ctx = canvas.getContext("2d");              // Get 2D drawing context

const width = (canvas.width = window.innerWidth);   // Set canvas width
const height = (canvas.height = window.innerHeight); // Set canvas height

// function to generate random number

function random(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min; // Return random int in range
}

// function to generate random RGB color value

function randomRGB() {
  return `rgb(${random(0, 255)},${random(0, 255)},${random(0, 255)})`; // Return random color string
}

class Ball {
  constructor(x, y, velX, velY, color, size) {
    this.x = x;         // X position
    this.y = y;         // Y position
    this.velX = velX;   // X velocity
    this.velY = velY;   // Y velocity
    this.color = color; // Ball color
    this.size = size;   // Ball radius
  }

  draw() {
    ctx.beginPath();                                      // Start new path
    ctx.fillStyle = this.color;                           // Set fill color
    ctx.arc(this.x, this.y, this.size, 0, 2 * Math.PI);   // Draw circle
    ctx.fill();                                           // Fill the circle
  }

  update() {
    if (this.x + this.size >= width) {   // Hit right edge
      this.velX = -Math.abs(this.velX);  // Bounce left
    }

    if (this.x - this.size <= 0) {       // Hit left edge
      this.velX = Math.abs(this.velX);   // Bounce right
    }

    if (this.y + this.size >= height) {  // Hit bottom edge
      this.velY = -Math.abs(this.velY);  // Bounce up
    }

    if (this.y - this.size <= 0) {       // Hit top edge
      this.velY = Math.abs(this.velY);   // Bounce down
    }

    this.x += this.velX; // Update X position
    this.y += this.velY; // Update Y position
  }

  collisionDetect() {
    for (const ball of balls) {
      if (!(this === ball)) {                           // Skip self
        const dx = this.x - ball.x;                     // X distance
        const dy = this.y - ball.y;                     // Y distance
        const distance = Math.sqrt(dx * dx + dy * dy);  // Calculate distance

        if (distance < this.size + ball.size) {        // If balls overlap
          ball.color = this.color = randomRGB();       // Change both colors
        }
      }
    }
  }
}

const balls = []; // Array to store all balls

while (balls.length < 25) { // Create 25 balls
  const size = random(10, 20); // Random size 10-20
  const ball = new Ball(
    // ball position always drawn at least one ball width
    // away from the edge of the canvas, to avoid drawing errors
    random(0 + size, width - size),
    random(0 + size, height - size),
    random(-7, 7),
    random(-7, 7),
    randomRGB(),
    size
  );

  balls.push(ball);
}

function loop() {
  ctx.fillStyle = "rgba(0, 0, 0, 0.25)"; // Semi-transparent black
  ctx.fillRect(0, 0, width, height);      // Draw trail effect

  for (const ball of balls) {
    ball.draw();           // Draw ball
    ball.update();         // Update position
    ball.collisionDetect(); // Check collisions
  }

  requestAnimationFrame(loop); // Next animation frame
}

loop(); // Start animation