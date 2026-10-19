**Task 2 — Display and animate the placeholder boxers**

Use the figures in `staticboxers` to create a minimal SpriteKit test scene.

**Goal**

Verify that both figures display correctly at phone size and remain aligned while playing a simple idle animation.

**Scene**

- Display two boxers facing each other on a shared ground line.
- Use a plain background with enough contrast to see every body part.
- Match their scale and ground alignment.
- Keep both figures fully visible in landscape orientation.
- Keep the original static assets intact.

**Idle animation**

Create a gentle breathing cycle from the editable body parts:

- Slight rise and fall of the torso and shoulders.
- Small coordinated movement of the gloves.
- Minimal head movement.
- Feet remain planted.
- Joints stay connected and limb lengths remain consistent.

Export four complete transparent frames per boxer. Use the same 512 × 512 canvas, origin, and baseline as the static figures. Play the frames as a repeating cycle lasting approximately 800 milliseconds.

Both palettes must use identical poses and timing. Mirror the second boxer at runtime.

**Review controls**

Provide simple debug controls to:

- Pause and resume.
- Step through individual frames.
- Replay at reduced speed.
- Toggle the ground line and figure origins.

**Acceptance criteria**

- Neither boxer drifts or changes size during playback.
- Feet remain on the ground without sliding.
- The transition from the last frame to the first is smooth.
- Both gloves remain readable at the intended display size.
- Mirroring preserves alignment.
- The scene runs on an iOS simulator or device; report which was checked.

Do not add movement controls, attacks, health, stamina, or opponent AI yet.

**Deliverables**

The runnable test scene, exported idle frames, editable animation source, and a short playback recording or preview.
