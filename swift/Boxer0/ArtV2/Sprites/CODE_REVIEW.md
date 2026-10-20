# SpriteSplitter edge review

The supplied code was reviewed; the original WPF project was not supplied or compiled. The Python cleanup is an executed, separate prototype for these nine existing exports, not a compiled C# patch.

## Why the current edges remain rough

All nine exported PNGs have binary alpha: every pixel is either0 or255. The flood fill removes neutral light background pixels but leaves partially blended boundary colors as opaque. These colors contain gray/white checkerboard mixed into the drawing, producing light fringes on dark backgrounds. Simply making more colors transparent can damage boot trim and glove highlights.

RemoveSpecksAndFringes changes rgbValues while using it to count neighbors. Later pixels therefore see earlier removals. Use an immutable source snapshot and a separate destination for each pass. The transparentNeighbors>=3 rule also misses a continuous fringe with only one or two transparent neighbors, and it can remove legitimate thin white detail.

Border flood fill cannot find checkerboard trapped inside closed gaps between limbs. These need checkerboard-aware segmentation or reviewed local masks; do not globally delete every white/gray pixel because white costume details are real artwork.

## Changes to make in C#

1. If the input already has correct transparency, preserve its original alpha, including intermediate values. Do not run color keying unnecessarily.
2. Separate background classification from foreground coverage. Flood fill gives a rough mask; a narrow edge band needs fractional alpha and color decontamination, not just alpha0.
3. Read each cleanup pass from a snapshot:

```csharp
byte[] source = (byte[])rgbValues.Clone();
// Read ALL color/alpha/neighbor decisions from source.
// Write results ONLY to rgbValues, then commit once at the end.
```

4. Use connected-component analysis to remove reviewed tiny disconnected islands. Do not erode the entire silhouette or remove all small bright pixels. For these nine images, islands of12 pixels or fewer were inspected and removed; that limit is specific to this resolution.
5. Restrict edge reconstruction to the outer boundary. Estimate the local matte and nearest dark outline color. The cleanup script uses C = alpha*F + (1-alpha)*B as an approximate coverage model. This cannot recover unknown original colors exactly; hard-keyed/low-resolution inputs remain imperfect.
6. Preview composited over both dark and light solid colors at native size and zoom. A checkerboard-only viewer can hide pale fringes.
7. Keep native resolution during extraction, then place on the production canvas using one consistent scale and root/baseline registration. Do not resize every pose to a fixed height independently.

## Other correctness issues

- Protect LockBits/UnlockBits with try/finally. Handle a negative stride by reading/writing logical rows with the signed stride; merely taking Abs(stride) is insufficient to preserve row orientation.
- Put the processing UI state reset in try/catch/finally. A processing exception currently leaves buttons disabled and may leak partially created bitmaps.
- Prevent picking a new sheet while export is reading _processedBitmaps, or export an independently owned snapshot. Otherwise the picker can dispose bitmaps being exported.
- A fixed3x3 grid is appropriate only for a verified3x3 source with clear gutters. Integer division discards remainder pixels. For exact partitioning, use x0=c*width/cols and x1=(c+1)*width/cols (similarly for rows), then crop width=x1-x0. This does not solve overlapping poses.

## Best source for clean results

Request individual PNGs with genuine transparent alpha, or layered/vector artwork, at the intended resolution. Ask for no painted checkerboard, no overlapping figures and clear margins. Inspect alpha numerically: a filename ending in.png does not establish transparency. Export PNG rather than JPEG, and avoid screenshots or repeated resizing. Enlarging a small source cannot restore missing line detail.

Perfect recovery from a flattened checkerboard is generally underdetermined: both original foreground color and coverage are unknown. Clean source alpha or a small manual contour pass is more dependable than increasingly aggressive thresholding.

## Current outputs

Cleaned/ contains conservative edge-cleaned copies at the original341x227 dimensions. Originals are unchanged. The script restores estimated fractional alpha on neutral edge pixels and removes reviewed tiny detached islands, while asserting that all original interior pixels remain identical. It does not realign poses, create new artwork or integrate game assets. Some grain/jaggedness remains in the low-resolution drawing; inspect edge_comparison.jpg before production use.
