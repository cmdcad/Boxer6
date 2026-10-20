# V2 production status

All prepared blue and orange sprites are integrated into the live catalog. Asset/source validation passes. Xcode compilation, execution of the 40 XCTest methods, and iPhone visual validation remain pending; see INTEGRATION.md.

| Source | Animation | Frames per fighter |
|---|---|---:|
| Stage A | Idle | 4 |
| Stage B | Advance / Retreat | 6 / 6 |
| Stage C | Guard / Guarded Advance / Guarded Retreat | 3 / 6 / 6 |
| Stage D | Jab / Cross / separate recovery poses | 6 / 8 / 1 / 1 |
| Stage E | Hit / Jab Block / Cross Block | 4 / 3 / 3 |
| Stage E | Knockdown / Down / Rise | 8 / 1 / 8 |
| Stage F | Orange palette variants of all above | 74 |

Production contract: transparent RGBA512 canvases, root(256,448), baseline448, right-facing source; orange mirrors at runtime. Preserve existing mechanics, timing, contact markers and recovery. Guarded walking now uses the existing travel-driven movement phase. Device review must check foot sliding and contact overlays; existing source softness and the collapse-to-Down transition remain visual limitations.

User approval: actual-upload Idle and ordinary footwork were explicitly approved. Later stages were prepared/repaired and integrated after the user instructed progression. Dedicated Cross transitions, fixed-foot compositing and orange palette production were authorized in chat.

Keep source artwork, final frames, active preparation/validation scripts, manifests and the original-art rollback archive. Task specifications under Tasks remain the mechanics reference. Legacy IdleAnimation art remains because historical validation and geometry checks still use it.
