---
name: figma-to-motion-page
description: Turn a Figma frame into an animated motion page in the sandbox repo. Use when the user gives a figma.com URL and wants it built as a motion/animation page, or wants a Figma design recreated with motion in the style of the other sandbox motion apps.
---

# Figma frame to sandbox motion page

Combine this with `sandbox-motion-timeline` (the animation engine) and `sandbox-ship-app` (homepage tile and release).

## 1. Read the design
1. Parse the URL: `fileKey` and `node-id` (`303-3911` becomes `303:3911`).
2. `create_session(fileKey, description)` first, and pass the returned `sessionId` on later Figma calls.
3. Load the `figma:figma-design-to-code` and `figma:figma-implement-motion` skills, then call `get_design_context` (with `skillNames`) and `get_motion_context` (`recursive: true`), plus `get_screenshot` for a reference image.
4. If `get_motion_context` returns `{"nodes":[]}` the frame has no animation. Say so and author the motion yourself from the static design, in the style of the other motion apps (see `sandbox-motion-timeline`). Do not invent motion silently.

## 2. Assets
- The returned asset URLs expire (about 7 days). `curl -sSL` each one into `<app>/assets/` and reference the local files. Never leave the temporary URLs in the page.
- Shrink big PNGs: `convert in.png -resize 256x256 -quality 82 out.webp` (product shots shown at about 40px in a 411px frame).
- Drop assets that are only mask shapes.

## 3. Reading the coordinates
- The design code is Tailwind with `mask-position-[-Xpx_-Ypx]` and a `mask-size` equal to the visible frame (e.g. 411.455 x 216.498). That mask rectangle is the real frame; the 498 x 253 outer div is not. An element with `mask-position -X -Y` sits at (X, Y) inside the frame, and anything past the frame edge is clipped. `get_screenshot` reports the true size in `original_width/height`.
- Build a fixed-size `#frame` (the mask size) with `overflow: hidden`, a corner radius and absolutely positioned children, then scale it to the stage with a JS `fit()` (`transform: scale(s)` with origin `0 0`, resized on `ResizeObserver`). Put sizes in the design's raw pixel values.
- Rotated wrappers (`rotate-[14deg]`) rotate the inner node about the wrapper's centre; place the file's own width/height at that centre.
- The design lists layers back to front: keep that z-order.

## 4. Type
The brand font (e.g. TT Mavenoid) isn't available. Use Inter 500/600 with `letter-spacing: -.01em` to `-.02em` and `white-space: nowrap` where the design is one line; check wrapping against the screenshot.

## 5. Verify with screenshots
Use Playwright (`NODE_PATH=$(npm root -g)`), not a guess:
- Open the page with `#clip`, `__rb.seek(t)` to the finished state (t=0 is the composed end state) and screenshot `#box`. Compare side by side with the Figma reference and fix offsets and wrapping.
- Then grab frames across the timeline (e.g. 2.0, 3.6, 4.9, 5.8) and tile them with `convert a.png b.png +append`, to check the sequence.
- Keep scratch files in the scratchpad directory, not the repo.
