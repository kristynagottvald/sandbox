---
name: motion-explainer
description: Build a looping animated product or concept explainer (screens, cursor, typing, illustrated characters) as a deterministic timeline in one HTML file. Use for Sander Troubleshoot, NLP Diagram, Agentic Storefront, Video Synopsis, Clearco motion style pieces.
---

# Motion explainer

Reference: `sander-troubleshoot`, `nlp-diagram`, `agentic-storefront`, `clearco-logistics-motion`.

- **One master timeline**, a function of time `T` (seconds), not scattered timeouts. Expose `window.__rb = {play, seek, pause, T}` so clips can be recorded deterministically (`play({from, speed, loop})`) and `#clip` mode starts clean.
- **Start state = first frame = loop point.** The still must look finished and intentional.
- **Do not fade screens or the main character in/out.** Swap places, slide or scale them; keep the previous screen visible behind the new one when that tells the story.
- **Things attached to an object move with it** (outline, cord, shadow). Static things stay still (the hand, sparkles if asked).
- **Seams:** use hard complementary masks, not feathered ones, where two illustrated layers meet; keep edges tidy and consistent margins on screens (check for gaps).
- **Interaction realism:** typed text, a pressed state on the button that "gets clicked", a hold (~3s) on the key screen so it can be read.
- **Illustrations:** small details (eye pupils, goggles) must be sized relative to the head; check zoomed in. Limbs/arms need smooth paths, not kinked ones.
- Keep the whole cycle ~9s so 1.4-1.75x playback fits the 6.5s home clip.
- Respect `prefers-reduced-motion`; finish with `rerecord-clip`.
