# Phase 3B — Orange guard, locomotion and bounce handoff

## Implementation
The Orange jab artwork remains V2 and the current cross is retained **as
provisional**, not approved as final. This pass changes only Orange's visual
bounce phase when leaving other actions; it does not replace images.

`IdleTestScene.swift` now restarts the approved 17-frame bounce at frame 0
(stance) on three transitions:
- Actual locomotion change from advance/retreat to idle.
- Guard release (after any existing block recoil has presentation priority).
- Completion of the physical punch recovery clock (jab or cross).

These are event-driven resets, **not** a reset every render tick. Bounce
advances normally at its existing 1.105-second loop while standing idle.
The reaction-completion handoff deliberately remains at frame 1, as before.
The change does not move roots, change sprite scales, retime punches, adjust
hitboxes, change CPU decisions or alter the existing cross.

## Mac verification
```bash
git pull origin master
python3 tools/audit_fighter_animations.py --markdown
```

Build and run in Xcode. Verify:
1. Orange advances, stops, and resumes bounce from its stance without a
   mid-cycle pop; retreat has the same behavior.
2. With CPU disabled, toggle Orange guard on and off. After guard release,
   bounce starts from its stance; while selected, the guard frames still win.
3. Enable CPU, observe Orange jab and retained cross, including misses and
   blocks. After physical recovery ends, Orange returns to bounce at stance.
4. Hit Orange during its jab or while recovering. The hit reaction retains
   priority and still hands off to bounce at the existing frame 1.
5. Confirm root positions and punch contact markers remain unchanged.
6. Pause/resume during guard, locomotion and recovery. No unrequested
   advancement or repeated frame-zero reset should occur.

## Known limits
- Source-level integration is committed, not Xcode-validated here.
- This fixes stale animation *phase* at handoffs, not pose differences
  between provisional guard/locomotion/cross artwork and approved bounce.
- Cross redraw remains a separate art task. No new heavy punch is introduced.

## Next step
Capture the most visible remaining mismatch by source/target clip pair.
If it is artwork-only, schedule that specific Orange asset set; if it is a
code/priority error, fix it before progressing to Phase 4.
