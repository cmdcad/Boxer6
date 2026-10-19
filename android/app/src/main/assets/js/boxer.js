class Boxer {
  constructor(name, x, dir, controller, level = 1) {
    this.name = name;
    this.x = x;
    this.defaultX = x;
    this.y = 225;
    this.dir = dir;
    this.controller = controller;
    this.isPlayer = controller === 'player';
    this.frames = null;
    this.currentFrame = null;
    this.bloodParticles = [];
    this.statusMessage = '';
    this.statusTimer = 0;
    this.spriteSizes = { punch: { w: 342, h: 346 }, uppercut: { w: 302, h: 346 }, hook: { w: 302, h: 346 } };
    this.stepSize = 10;
    this.maxHealth = 90;
    this.health = this.maxHealth;
    // --- STAMINA PROPERTIES ---
    this.maxStamina = 100;
    this.stamina = this.maxStamina;
    this.isStunned = false;
    // --- END STAMINA ---
    this.lastHitTime = 0;
    this.punching = false;
    this.attackType = 'punch';
    this.blocking = false;
    this.frameIndex = 0;
    this.lastStepTime = 0;
    this.animationInterval = 150;
    this.stunnedUntil = 0;
    this.level = level;
    this.isChargingAttack = false;
    this.attackChargeCounter = 0;
    this.uppercutsLeft = 0;
    this.hooksLeft = 0;
    this.resetSpecialMoves();
  }

  resetSpecialMoves() {
    this.isChargingAttack = false;
    this.attackChargeCounter = 0;
    this.uppercutsLeft = 1 + Math.floor(this.level / 5);
    this.hooksLeft = 10;
  }

  setStatus(message, duration = 1000) {
    this.statusMessage = message;
    this.statusTimer = performance.now() + duration;
  }

  draw() {
    if (!this.currentFrame) return;
    ctx.save();
    ctx.translate(this.x, this.y);
    ctx.scale(this.dir, 1);
    let sw = 232, sh = 345;
    if (this.currentFrame === this.frames.punch || this.currentFrame === this.frames.uppercut || this.currentFrame === this.frames.hook) {
      sw = this.spriteSizes[this.attackType].w;
      sh = this.spriteSizes[this.attackType].h;
    }

    const displayH = 150; // Increased from 120
    const scale = displayH / sh;
    const displayW = sw * scale;
    const drawX = -displayW / 2;
    const drawY = -displayH;
    ctx.drawImage(this.currentFrame, drawX, drawY, displayW, displayH);
    ctx.restore();
    this.bloodParticles = this.bloodParticles.filter(p => p.life > 0);
    this.bloodParticles.forEach(p => { p.update(); p.draw(); });
  }

/*TODO
UPDATE STUNNED FRAMES
ADD BLOCKED FRAME

*/
  updateFrame() {
    if (this.isStunned) {
      // You can add a specific stun frame if you have one
      this.currentFrame = this.frames.w3; // Example: use a tired-looking frame
      return;
    }
    if (this.punching) {
      let frame = this.frames[this.attackType];
      if (!frame || !frame.complete || frame.naturalWidth === 0) frame = this.frames.punch;
      this.currentFrame = frame;
      return;
    }
    if (this.blocking) {
      this.currentFrame = this.frames.block;
      return;
    }
    if (this.frameIndex === 0) this.currentFrame = this.frames.w1;
    else if (this.frameIndex === 1) this.currentFrame = this.frames.w2;
    else this.currentFrame = this.frames.w3;
  }

  stepForward(time) {
    if (this.blocking || this.isStunned || this.stamina < STAMINA_COST.STEP) return; // Added this.blocking check
    this.stamina -= STAMINA_COST.STEP;
    this.x += this.dir * this.stepSize;
    this.frameIndex = (this.frameIndex + 1) % 3;
    this.lastStepTime = time;
  }


    stepBackward(time) {
      if (this.blocking || this.isStunned || this.stamina < STAMINA_COST.STEP) return; // Added this.blocking check
      this.stamina -= STAMINA_COST.STEP;
      this.x -= this.dir * this.stepSize;
      this.frameIndex = (this.frameIndex + 1) % 3;
      this.lastStepTime = time;
    }


  punch(type = 'punch') {
    if (this.isStunned || this.punching || (performance.now() < this.stunnedUntil)) return;

    const cost = STAMINA_COST[type.toUpperCase()];
    if (this.stamina < cost) {
      this.setStatus("No Stamina!", 800);
      return;
    }

    if (type === 'uppercut' && this.uppercutsLeft <= 0) {
      this.setStatus("No Uppercuts!", 800);
      return;
    }

    if (type === 'hook' && this.hooksLeft <= 0) {
      this.setStatus("No Hooks!", 800);
      return;
    }

    this.stamina -= cost;
    if (this.stamina <= 0) {
      this.isStunned = true;
      this.stamina = 0; // Prevent negative stamina
      this.setStatus("STUNNED!", 2000);
    }

    this.blocking = false; // Drop block when attacking
    this.attackType = type;
    this.punching = true;
    setTimeout(() => { this.punching = false; }, 300);
  }

  uppercut() { this.punch('uppercut'); }
  hook() { this.punch('hook'); }
  toggleBlock() {
    if (this.isStunned) return; // Can't block while stunned
    this.blocking = !this.blocking;
    this.setStatus(this.blocking ? 'Blocking!' : 'Unblocking!');
  }

  takeDamage(amount, hitX, pushAmount = 0) {
    if (this.blocking) {
      this.setStatus("Blocked!", 500);
      return;
    }
    this.health = Math.max(0, this.health - amount);
    for (let i = 0; i < 5; i++) {
      this.bloodParticles.push(new Particle(hitX, this.y - 60));
    }
    this.x += this.dir * -pushAmount;
  }

  updateAI(opponent, time) {
    if (this.isStunned || time < this.stunnedUntil) {
      this.isChargingAttack = false;
      this.attackChargeCounter = 0;
      if (this.isStunned) this.setStatus('Stunned!', 500);
      else this.setStatus('Stunned!', this.stunnedUntil - time);
      return;
    }
    const distance = Math.abs(this.x - opponent.x);

       if (this.blocking) {
          // If currently blocking, have a small chance to stop.
          if (Math.random() < 0.02) { // 2% chance per frame to stop blocking
            this.toggleBlock();
          }
          // Don't attack or move while blocking.
          return;
        }

    if (this.isChargingAttack) {
      this.attackChargeCounter++;
      this.setStatus("Winding up...", 350); // Using the longer duration
      if (this.attackChargeCounter >= 20) {
        const rand = Math.random();
        let randomAttack = 'punch';
        if (rand > 0.5 && this.uppercutsLeft > 0) randomAttack = 'uppercut';
        else if (rand > 0.9 && this.hooksLeft > 0) randomAttack = 'hook';
        this[randomAttack]();
        this.isChargingAttack = false;
        this.attackChargeCounter = 0;
      }
      return;
    }
    if (distance > MIN_DISTANCE && time - this.lastStepTime > 400) {
      this.stepForward(time);
    } else if (distance-20 < MIN_DISTANCE && Math.random() < 0.01) {
      this.isChargingAttack = true;
      this.attackChargeCounter = 0;
    }

   // Decide to start blocking (only if not already attacking/charging)
     if (distance < 100 && Math.random() < 0.01) { // Increased block chance to 1%
       this.toggleBlock();
     }
  }
}