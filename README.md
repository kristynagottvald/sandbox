# Sandbox

A personal lab for experimental **brand, web and motion** work. Each project is a small, self-contained exploration: a looping motion system, an interactive generator, a landing page or email concept, or a quick product mockup. Most are built around a brand's visual language (type, colour, grid, geometry) and push it into something that moves or that you can play with.

## See it live

**https://kristynagottvald.github.io/sandbox/**

The home page is the best way to browse. Every project is a tile that plays a 6 second looping preview, newest first. Click a tile to open the full project.



## How it's built

- **One folder per project**, each with a single `index.html`. No build step, no framework, no bundler; open the file and it runs.
- Each folder also has `thumb.webp` (the 6 second looping clip, 960×540) and `thumb.png` (its first frame) for the home page tile.
- The home page (`index.html`, `styles.css`, `script.js`) draws its tiles from `apps.json`, ordered newest first.
- Every project has a "Sandbox / Back to all projects" bar linking back to the home page.
