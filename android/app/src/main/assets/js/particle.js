
class Particle {
const ctx = ctx
  constructor(x, y) {
    this.x = x; this.y = y; this.size = Math.random() * 2 + 1;
    this.speedX = Math.random() * 3 - 1.5; this.speedY = Math.random() * -3 - 1;
    this.life = 1; this.maxLife = Math.random() * 50 + 50;
  }
  update() {
    this.x += this.speedX; this.y += this.speedY; this.speedY += 0.1;
    this.life -= 1 / this.maxLife;
  }
  draw() {
    ctx.fillStyle = `rgba(255, 0, 0, ${this.life})`;
    ctx.beginPath(); ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2); ctx.fill();
  }
}