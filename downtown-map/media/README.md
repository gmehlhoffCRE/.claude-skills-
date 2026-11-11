# Flyover video + base image (Google Earth Studio)

Put two files here, then set them at the top of the script in `index.html`:

```js
const AERIAL_IMAGE = "media/orbit-end.jpg";   // last frame of the video
const INTRO_VIDEO  = "media/orbit.mp4";       // the orbit / flyover
```

The video plays once when the page opens, fades into the still image, and the hotspots appear.
A "Replay flyover" button stays in the corner of the map.

## Turning Earth Studio frames into these files

Earth Studio exports a folder of numbered JPEGs. Match the file name pattern to your export
(e.g. `downtown_000.jpeg` → `downtown_%03d.jpeg`).

```bash
ffmpeg -framerate 30 -i downtown_%03d.jpeg -c:v libx264 -pix_fmt yuv420p -crf 22 -movflags +faststart orbit.mp4
```

The still is simply the **last frame** of the export. Copy it and rename it `orbit-end.jpg`.

Keep the video under ~50 MB (shorter clip or higher `-crf` value = smaller file).
Keep Google's on-screen attribution visible in both files.
