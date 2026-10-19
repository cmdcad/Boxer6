

// --- Asset Loading ---
function loadImage(src) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => resolve(img);
    img.onerror = reject;
    img.src = src;
  });
}

async function loadFrames() {
  const frameNames = ['w1', 'w2', 'w3', "w4", 'punch',  'block'];

  const frames = {};
  for (const name of frameNames) {
    try {
      // Corrected path for Android assets
      frames[name] = await loadImage(`file:///android_asset/frames/${name}.png`);
    } catch (e) {
      console.error(`Failed to load frame: ${name}`, e);
    }
  }
  return frames;
}


class Particle {
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

// --- Canvas and Context ---
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');

// --- Global Game State ---
// --- STAMINA CONSTANTS ---
const STAMINA_REGEN_RATE = 15; // Stamina points per second
const STAMINA_COST = {
  PUNCH: 15,
  HOOK: 25,
  UPPERCUT: 30,
  STEP: 2,
  BLOCK_PER_SECOND: 30
};

const STUN_RECOVERY_THRESHOLD = 25; // Stamina needed to recover from stun
let lastStaminaRegenTime = 0;const MIN_DISTANCE = 50;
// --- END STAMINA ---
const player = new Boxer("Player", 150, +1, 'player');
const cpu = new Boxer("CPU", 450, -1, 'ai');
let gameOver = false;
let gamePaused = false; // Add this for pausing between rounds
let gameHasStarted = false; // Add this new global variable near the top with the others
let currentRound = 1;
let roundTimeLeft = 30;
let roundTimerInterval;
const keys = {};


// --- DOM Elements ---
const playerLvlEl = document.getElementById('playerLvl');
const cpuLvlEl = document.getElementById('cpuLvl');
const roundTimerEl = document.getElementById('roundTimer');
const roundTextEl = document.getElementById('roundText');
const playerHealthFill = document.getElementById('playerHealthFill');
const cpuHealthFill = document.getElementById('cpuHealthFill');
const playerStaminaFill = document.getElementById('playerStaminaFill');
const cpuStaminaFill = document.getElementById('cpuStaminaFill');
const gameOverEl = document.getElementById('gameOver');
const gameOverText = document.getElementById('gameOverText');
// --- DOM Elements ---
const restartBtn = document.getElementById('restartBtn');
const startPauseBtn = document.getElementById('btn-start'); // Get the start button


// --- Game Logic Functions ---
function updateHud() {
  if (playerHealthFill) playerHealthFill.style.width = (player.health / player.maxHealth * 100) + '%';
  if (cpuHealthFill) cpuHealthFill.style.width = (cpu.health / cpu.maxHealth * 100) + '%';
  if (playerStaminaFill) playerStaminaFill.style.width = (player.stamina / player.maxStamina * 100) + '%';
  if (cpuStaminaFill) cpuStaminaFill.style.width = (cpu.stamina / cpu.maxStamina * 100) + '%';
  if (playerLvlEl) playerLvlEl.textContent = `Player Lvl: ${player.level}`;
  if (cpuLvlEl) cpuLvlEl.textContent = `CPU Lvl: ${cpu.level}`;
  if (roundTextEl) roundTextEl.textContent = `Round ${currentRound}`;
  if (roundTimerEl) roundTimerEl.textContent = `Time: ${roundTimeLeft}`;
}

function startRoundTimer() {
  clearInterval(roundTimerInterval); // Only clear the timer, don't pause the game
  roundTimeLeft = 30;
  updateHud();
  roundTimerInterval = setInterval(() => {
    roundTimeLeft--;
    updateHud();
    if (roundTimeLeft <= 0) {
      endRound();
    }
  }, 1000);
}


function stopRoundTimer() {
  clearInterval(roundTimerInterval);
  gamePaused = true; // Pause the game whenever a round stops
}


function endRound() {
  stopRoundTimer(); // This will pause the game

  // Check for a winner if max rounds are reached
  if (currentRound >= 15) {
    if (player.health > cpu.health) {
      gameOverText.textContent = 'You Win by Decision!';
    } else if (cpu.health > player.health) {
      gameOverText.textContent = 'You Lose by Decision!';
    } else {
      gameOverText.textContent = 'Draw!';
    }
    gameOver = true;
    gameHasStarted = false; // Game is over
    startPauseBtn.textContent = 'Start'; // Reset button text
    gameOverEl.style.display = 'flex';
    return;
  }

  // If not max rounds, set up for the next round
  gameOverText.textContent = `End of Round ${currentRound}`;
  restartBtn.textContent = 'Next Round'; // Change button text
  gameOverEl.style.display = 'flex';
}



function togglePause() {
  // If the game hasn't started yet, or it's over, start a new game
  if (!gameHasStarted || gameOver) {
    resetGame();
    return;
  }

  // Otherwise, toggle the pause state
  gamePaused = !gamePaused;

  if (gamePaused) {
    startPauseBtn.textContent = 'Resume';
    // When paused, we also need to stop the round timer
    clearInterval(roundTimerInterval);
  } else {
    startPauseBtn.textContent = 'Pause';
    // When resuming, restart the round timer and the animation loop
    startRoundTimer();
    requestAnimationFrame(update);
  }
}

// In main.js

function drawStatusNotifications(now) {
  ctx.save();
  ctx.fillStyle = 'white';
  ctx.font = 'bold 22px Arial';
  ctx.textAlign = 'center';
  ctx.shadowColor = 'black';
  ctx.shadowBlur = 3;

  if (!gameHasStarted) {
    ctx.font = 'bold 30px Arial'; // Use a larger font for the start message
    ctx.fillText('PRESS START', canvas.width / 2, (canvas.height / 2) );
  } else {
    // Only draw these if the game has started
    if (player.statusTimer > now) ctx.fillText(player.statusMessage, player.x, player.y - 140);
    if (cpu.statusTimer > now) ctx.fillText(cpu.statusMessage, cpu.x, cpu.y - 140);
    if (player.blocking) ctx.fillText('Player Blocking', 150, 20);
    if (cpu.blocking) ctx.fillText('CPU Blocking', 450, 20);
  }

  ctx.restore();
}


function drawRingBackground() {
  // Draw the ring floor, starting from the boxer's feet (y=215) down to the bottom of the canvas
  ctx.fillStyle = '#8B4513';
  ctx.fillRect(0, 230, 600, 85);
}

function drawRingForeground() {
  ctx.strokeStyle = '#D2691E';
  ctx.lineWidth = 4;
  ctx.beginPath();
  // Draw 3 ropes, adjusted for the new taller posts
  ctx.moveTo(20, 150); // Top rope
  ctx.lineTo(580, 150);
  ctx.moveTo(20, 180); // Middle rope
  ctx.lineTo(580, 180);
  ctx.moveTo(20, 210); // Bottom rope
  ctx.lineTo(580, 210);
  ctx.stroke();

  // Draw taller ring posts
  ctx.fillStyle = '#8B4513';
  ctx.fillRect(0, 140, 20, 160); // Left post
  ctx.fillRect(580, 140, 20, 160); // Right post
}

// --- Main Execution Block ---
let update; // To be defined after assets are loaded

function resetGame() {
  // --- If the game is paused between rounds, just resume for the next round ---
  if (gamePaused && !gameOver) {
    currentRound++;
    player.resetSpecialMoves();
    cpu.resetSpecialMoves();
    player.x = player.defaultX;
    cpu.x = cpu.defaultX;
    gamePaused = false;
      player.bloodParticles = [];
      cpu.bloodParticles = [];
      player.blocking = false;
      cpu.blocking = false; // <-- ADD THIS LINEplayer.statusMessage = ''; cpu.statusMessage = '';
    gameOverEl.style.display = 'none';
    startRoundTimer();
    requestAnimationFrame(update); // Resume the game loop
    startPauseBtn.textContent = 'Pause'; // Ensure button says "Pause" for the new round
    return; // Exit the function here
  }

  // --- Otherwise, perform a full, clean reset for a new game ---
  gameHasStarted = true; // Mark that the game is now in progress
  startPauseBtn.textContent = 'Pause'; // Change button text to "Pause"

  const savedLevel = localStorage.getItem('playerLevel');
  player.level = savedLevel ? parseInt(savedLevel, 10) : 1;

  player.health = player.maxHealth;
  cpu.health = cpu.maxHealth;
  player.stamina = player.maxStamina; // Reset stamina
  cpu.stamina = cpu.maxStamina;     // Reset stamina
  player.isStunned = false;         // Reset stun
  cpu.isStunned = false;          // Reset stun
  player.x = player.defaultX;
  cpu.x = cpu.defaultX;
  player.resetSpecialMoves();
  cpu.resetSpecialMoves();
  player.bloodParticles = []; cpu.bloodParticles = [];
  player.blocking = false;
  cpu.blocking = false;
  player.statusMessage = ''; cpu.statusMessage = '';
  player.stunnedUntil = 0; cpu.stunnedUntil = 0;

  gameOver = false;
  gamePaused = false;
  currentRound = 1;
  restartBtn.textContent = 'Restart'; // Ensure button text is correct
  if (gameOverEl) gameOverEl.style.display = 'none';

  clearInterval(roundTimerInterval);
  startRoundTimer();
  updateHud();

  // Start the animation loop
  requestAnimationFrame(update);
}


// Attach all event listeners once
restartBtn.addEventListener('click', resetGame);
startPauseBtn.addEventListener('click', togglePause); // Correct listener
document.getElementById('btn-left').addEventListener('click', () => player.stepBackward(performance.now()));
document.getElementById('btn-right').addEventListener('click', () => player.stepForward(performance.now()));
document.getElementById('btn-punch').addEventListener('click', () => player.punch());
document.getElementById('btn-uppercut').addEventListener('click', () => player.uppercut());
document.getElementById('btn-hook').addEventListener('click', () => player.hook());
document.getElementById('btn-block').addEventListener('click', () => player.toggleBlock());
document.getElementById('btn-settings').addEventListener('click', () => alert('Settings not implemented.'));

document.addEventListener('keydown', e => {
  const key = e.key.toLowerCase();
  if (!keys[key]) {
    keys[key] = true; const now = performance.now();
    if (key === ' ' || key === 'spacebar') { player.punch(); e.preventDefault(); }
    else if (key === 'u') { player.uppercut(); } else if (key === 'h') { player.hook(); }
    else if (key === 'b') { player.toggleBlock(); } else if (key === 'd' || key === 'arrowright') { player.stepForward(now); }
    else if (key === 'a' || key === 'arrowleft') { player.stepBackward(now); }
  }
});
document.addEventListener('keyup', e => { keys[e.key.toLowerCase()] = false; });

// Load assets, then define the main loop and start the game
loadFrames().then(frames => {
  player.frames = frames;
  cpu.frames = frames;

  // Define the main game loop
  update = function (time) {
    if (gamePaused) return; // Add this line to freeze the game
    const now = time || performance.now();
    ctx.clearRect(0, 0, 600, 300);
    drawRingBackground();

    // --- STAMINA REGENERATION ---
    if (now - lastStaminaRegenTime > 1000) {
      const regenAmount = STAMINA_REGEN_RATE;
      player.stamina = Math.min(player.maxStamina, player.stamina + regenAmount);
      cpu.stamina = Math.min(cpu.maxStamina, cpu.stamina + regenAmount);

      // Check for stun recovery
      if (player.isStunned && player.stamina >= STUN_RECOVERY_THRESHOLD) {
        player.isStunned = false;
        player.setStatus("Recovered!", 1000);
      }
      if (cpu.isStunned && cpu.stamina >= STUN_RECOVERY_THRESHOLD) {
        cpu.isStunned = false;
        cpu.setStatus("Recovered!", 1000);
      }
      lastStaminaRegenTime = now;
    }

    // --- END STAMINA REGENERATION ---
    if (!gameOver) {
      // Player Input
      if ((keys["d"] || keys["arrowright"]) && now - player.lastStepTime > player.animationInterval) player.stepForward(now);
      else if ((keys["a"] || keys["arrowleft"]) && now - player.lastStepTime > player.animationInterval) player.stepBackward(now);

      // AI Logic
      cpu.updateAI(player, now);

      // Collision
      if (Math.abs(cpu.x - player.x) < 20) { if (player.x < cpu.x) player.x = cpu.x - 20; else cpu.x = player.x + 20; }

      // Player Hits CPU
      if (player.punching) {
        let dist = Math.abs(player.x - cpu.x);
        let damage = 1, stunDuration = 0, pushAmount = 0;
        if (player.attackType === 'uppercut') { if (dist >= 70) dist = 999; damage = 3; stunDuration = 4000; pushAmount = 20; }
        else if (player.attackType === 'hook') { if (dist >= 120) dist = 999; damage = 2; stunDuration = 2000; pushAmount = 10; }
        if (dist < 90 && now - player.lastHitTime > 250) {
          const hitX = cpu.x + (player.dir > 0 ? -30 : 30);
          cpu.takeDamage(damage, hitX, pushAmount);
          if (stunDuration > 0) cpu.stunnedUntil = now + stunDuration;
          if (player.attackType === 'uppercut') player.uppercutsLeft--;
          if (player.attackType === 'hook') player.hooksLeft--;
          cpu.setStatus(player.attackType.charAt(0).toUpperCase() + player.attackType.slice(1) + ' Hit!');
          player.lastHitTime = now;
        }
      }

      // CPU Hits Player
      if (cpu.punching) {
        let dist2 = Math.abs(player.x - cpu.x), damage2 = 1, pushAmount2 = 0;
        if (cpu.attackType === 'uppercut') { if (dist2 >= 70) dist2 = 999; damage2 = 3; pushAmount2 = 20; }
        else if (cpu.attackType === 'hook') { if (dist2 >= 120) dist2 = 999; damage2 = 2; pushAmount2 = 10; }
        if (dist2 < 90 && now - cpu.lastHitTime > 250) {
          const hitX = player.x + (cpu.dir > 0 ? -30 : 30);
          player.takeDamage(damage2, hitX, pushAmount2);
          if (cpu.attackType === 'uppercut') cpu.uppercutsLeft--;
          if (cpu.attackType === 'hook') cpu.hooksLeft--;
          player.setStatus(cpu.attackType.charAt(0).toUpperCase() + cpu.attackType.slice(1) + ' Hit!');
          cpu.lastHitTime = now;
        }
      }

      // Game Over Check
      if (player.health <= 0) {
        gameOver = true;
        gameOverText.textContent = 'You Lose!';
        gameOverEl.style.display = 'flex';
        stopRoundTimer();
        gameHasStarted = false; // Game is over
        startPauseBtn.textContent = 'Start';
      } else if (cpu.health <= 0) {
        gameOver = true;
        gameOverText.textContent = 'You Win!';
        gameOverEl.style.display = 'flex';
        stopRoundTimer();
        player.level++;
        // Save the new level to localStorage
        localStorage.setItem('playerLevel', player.level);
        gameHasStarted = false; // Game is over
        startPauseBtn.textContent = 'Start'; // Reset button text
      }
    }

    // Drawing
    player.updateFrame();
    cpu.updateFrame();
    player.draw();
    cpu.draw();
    drawRingForeground();
    updateHud();
    drawStatusNotifications(now);

    // Continue the loop
    if (!gameOver) requestAnimationFrame(update);
  };

   ctx.clearRect(0, 0, 600, 300);
    drawRingBackground();
    player.updateFrame(); // Set initial frames
    cpu.updateFrame();
    player.draw();
    cpu.draw();
    drawRingForeground();
    updateHud();
    drawStatusNotifications(performance.now());

});

