# Stage E — blue hit reaction, supplied-art preparation

Four prepared frames at60ms each:240ms total. Source order is latest/02,04,03,01: initial recoil, peak backward recoil, torso recovery and settling. The forward-hunch05/06 alternatives are not mixed into this backward-recoil clip. Production names: frames/hit_react_a_0.png through3.png. Live assets are unchanged.

No image generation was used. The selected originals and conservatively cleaned versions are retained under source/. Originals in ArtV2/latest remain unchanged. The existing scripted cleanup reconstructs estimated fractional alpha on pale boundary pixels; connected-component selection removes detached head/ground marks. It does not invent missing source contours.

Every upper body uses a common1.48 scale. Reviewed source belt centers control translation, not independent bounding-box fitting. Source-specific sloping waist masks preserve the tilted abdomen; explicit arm rectangles keep gloves/forearms from being cut by those masks. They are recorded in manifest.json. A small approved Idle abdomen region joins the waist to the original lower body. Recoiling elbows overlap the upper hip; all pixels fromy300 downward, including all legs and boots, remain exactly the approved Idle. This avoids reliance on the tightly cropped source boots and prevents foot sliding in this stationary reaction.

Canvas512x512 RGBA, right-facing, root(256,448), baseline448. hit_reaction.png is the exact4-frame APNG. hit_reaction_to_idle.png adds approved Idle after240ms. hit_reaction_gameplay.gif is a gameplay-size review preview with a400ms Idle hold for readability. alignment_sheet.png shows all poses and guides; guides are not in the production PNGs.

Reproduce from the project root using prepare_hit_reaction.py then validate_hit_reaction.py. Both executed successfully on2026-10-20. Checks pass for four distinct frames, dimensions/alpha/margins, a single significant silhouette, baseline, exact legs/feet equality, checksums, actual APNG/GIF timing and exact approved Idle at the end of the APNG.

Limitations: supplied images are low resolution, binary-keyed and tightly cropped. Some hard hair edges/grain remain; source facial/shading details are softer and differ from approved Idle. Mask/waist joins and the strength of the recoil need visual review. No full-frame pose redraw, Swift changes, live integration, XCTest or SpriteKit/iPhone execution occurred. These checks do not establish final device acceptance.

Status: hit-reaction preview prepared, awaiting visual review. Stage E remains incomplete: block recoil, matching Knockdown, Down and Rise preparation are separate work.
