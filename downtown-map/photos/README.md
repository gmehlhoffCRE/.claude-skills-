# Building photos

Drop one photo per building in this folder, named exactly:

| Building | File name |
|---|---|
| 910 Louisiana | `910-louisiana.jpg` |
| 1000 Louisiana | `1000-louisiana.jpg` |
| 1111 Bagby | `1111-bagby.jpg` |
| 700 Louisiana | `700-louisiana.jpg` |
| Allen Center | `allen-center.jpg` |
| 717 Texas | `717-texas.jpg` |

Landscape photos around 1200 × 800 work best. They appear automatically on the hover card,
the building detail page and the matrix. Until a photo is added, a placeholder shows.

## Keeping the single HTML file self-contained

`index.html` carries its own embedded copy of these photos, so it works even when it's
opened or shared without this folder. After replacing a photo here, refresh the embedded copies:

```bash
python3 downtown-map/tools/embed_photos.py
```

(Requires ffmpeg.)
