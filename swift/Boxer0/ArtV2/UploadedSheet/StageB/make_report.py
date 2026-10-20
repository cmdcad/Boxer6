from pathlib import Path
import json
import zipfile

ROOT=Path(__file__).resolve().parent
manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
results=json.loads((ROOT/'validation_results.json').read_text(encoding='utf-8'))
rows=[]
for f in manifest['frames']:
    m=f['measurements']
    rows.append(f"| {f['clip']} {f['index']+1} | {m['bounds']} | {f['horizontal_registration']} | {f['vertical_registration']} | {m['rear']['ground_gap']} / {m['lead']['ground_gap']} |")
slip_rows=[]
for clip,phases in manifest['plant_slip_diagnostic'].items():
    for phase in phases:
        slip_rows.append(f"- {clip}, {phase['support']} support, frames {phase['frames']}: {phase['range_px']:.2f} preview pixels.")
report='''# Boxer0 V2 — Stage B actual-upload blue footwork

Stage A actual-upload Idle was approved in chat. This package continues that selected compact boxer, not the earlier superseded alternative character. The approved cleaned Idle provides identity; cropped Advance/Retreat strips from the uploaded sheet provide pose reference. Frames were reconstructed/refined with built-in imagegen because neighboring source poses touch/overlap and cannot be cleanly grid-sliced. They are not claimed to be untouched pixel cutouts.

## Deliverables

- frames/advance_a_0.png ... advance_a_5.png: six individual right-facing512x512 transparent RGBA PNGs.
- frames/retreat_a_0.png ... retreat_a_5.png: six individual right-facing512x512 transparent RGBA PNGs.
- advance_preview.png and retreat_preview.png: transparent APNGs, six80ms frames each,480ms looping.
- advance_gameplay.gif and retreat_gameplay.gif: approximately160px visible character height with a review-only scrolling ground grid.
- movement_preview.gif: both gameplay-size loops side by side. Advance is left; Retreat is right.
- alignment_sheet.png: root/baseline review guides. Labels and ground graphics are absent from the exported individual frames.
- manifest.json: exact selected sources, timing, checksums, planned phases, measured sole points and registration offsets.
- prompts.json and correction_prompts.json: built-in generation/edit prompt records; source/ retains generated/refined candidates.
- export_footwork.py, validate_footwork.py and validation_results.json: repeatable export, executed technical checks and motion review flags.

## Frame and motion contract

Both clips retain6 frames over480ms. Canvas512x512; right-facing; origin/ground root(256,448); support baseline448. No source art is individually fitted or warped. Every frame uses the same scale as the approved Idle and the same starting canvas transform.

Advance steps with the front/right foot first, then the rear foot follows. Retreat steps with the rear/left foot first, then the front follows. Each includes swing, landing and follow-through; no foot crossing. Gloves remain in the ordinary boxing stance. These are normal footwork clips, not guarded-walking artwork.

The clips legitimately share their wide double-plant and narrow closing stance because both directions pass through those same static configurations. Each clip still has six unique rendered poses. This is not arbitrary padding or a change to the future eight-frame Cross requirement. The Cross correction remains: create two genuine transitions when that production stage is reached.

## Root and planted-foot registration

Raw AI pose outputs do not numerically lock feet. Several candidates were rejected/corrected for wrong foot support, excessive height/scale, or an over-high swing. Export uses bounded vertical placement to put the named support sole on the baseline, and horizontal stance registration to coordinate the drawn planted sole with the existing root travel. Registration changes placement, never body proportions or image scale. The sprite canvas origin stays(256,448); there is no independent net image travel added across a loop.

Calibration:100 scene points/sec,0.5 sprite scale,80ms per frame ->8 scene points (16 canvas pixels) root travel per frame. The registration aligns sole-midpoint samples to that travel, including double-plant phases and the loop wrap. This makes the preview's ground grid a useful diagnostic rather than a decorative background.

| Frame | Ink bounds [left,top,right,bottom) | Horizontal registration | Vertical registration | Rear / lead ground gap |
|---|---|---:|---:|---|
'''+ '\n'.join(rows)+'''

Negative ground-gap values would indicate ink below baseline. Slight gap on the second sole of a double-plant stance can reflect a tilted boot/antialias edge. Measurements use alpha>=32; fringe pixels are not anatomical landmarks.

Measured support-sole midpoint ranges under the preview calibration (frame-1 denotes the preceding cycle's final pose):

'''+ '\n'.join(slip_rows)+'''

These are sampled image-space diagnostics, not proof of zero sliding on every frame or device. Foot rolling, toe shape and ankle placement are not a skeletal contact rig. Registration creates visible weight shifts and head/hip bob; assess their smoothness in the actual loop. Generated ink, laces, clothing folds and muscle shading can vary slightly between poses.

## Validation results and limitations

Executed export_footwork.py and validate_footwork.py. Technical checks pass: twelve512px true-alpha PNGs, six unique poses per clip, transparent margins, uncropped silhouettes, front/rear ordering, checksums and six80ms frames (480ms) in each GIF/APNG. Motion-review warnings, if any, are listed in validation_results.json.

Visual review inspected generated lift/follow-through poses, corrected landings, and the final alignment sheet. The original uploaded sheet's baked checkerboard is not exported. All art remains outside live Assets.xcassets. Swift gameplay, movement speed, contacts, guard rules, damage, existing animation timings and build label10A are unchanged. No XCTest execution is claimed: no integration occurred, and Xcode/Apple SDKs are unavailable on this Windows host.

SpriteKit/iPhone playback remains unverified. Actual fighter scale varies with viewport; CPU base speed is65 rather than the blue preview's100. This preview calibration does not establish correct foot locking for every scene scale or the later orange variants. Future integration must evaluate the visual stride against actual root travel for both fighters, without altering gameplay movement to disguise poor alignment. Body bob, lateral weight shift, minor ink/shading changes and foot rolling remain artistic-review points. The low-swing Advance correction is selected; the earlier high-step candidate is retained only as rejected source history. Pose registration can move the torso relative to the existing fixed target rectangle, so body/target alignment must also be checked before integration. No full production/device acceptance is claimed from asset checks alone.

## Review progression

Review the two loops here in chat first; they are not installed in the app yet. Stage C (Guard and guarded movement), punches and orange variants are not part of this package. Keep the working sprites active until the staged assets are approved and integration is ready for regression testing.

Tool provenance: built-in imagegen with transparent_background=true. Pillow/numpy are used only for requested uniform canvas export, bounded pose registration, measurement, previews and packaging; no painted body-part warping or synthetic leg drawing is performed by the exporter. Full prompts and selected source paths are retained.
'''
(ROOT/'README.md').write_text(report,encoding='utf-8')
with zipfile.ZipFile(ROOT/'uploaded_blue_footwork_stage_b.zip','w',zipfile.ZIP_DEFLATED) as archive:
    for file in ROOT.rglob('*'):
        if file.is_file() and file.suffix!='.zip' and '__pycache__' not in file.parts:
            archive.write(file,file.relative_to(ROOT))
print('Saved Stage B review report and ZIP.')
