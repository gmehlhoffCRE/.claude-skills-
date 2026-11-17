"""Build the single-file page: inlines the Cresa logo, map style and the CoStar building photos."""
import base64, json, pathlib
D = pathlib.Path(__file__).parent
photos = [{"a": p["address"], "n": p["name"],
           "src": "data:image/jpeg;base64," + base64.b64encode((D / p["file"]).read_bytes()).decode()}
          for p in json.loads((D / "photos/index.json").read_text())]
html = (D / "src/template.html").read_text()
html = html.replace("__LOGO__", (D / "src/logo.datauri").read_text().strip())
html = html.replace("__MAPSTYLE__", (D / "src/map_style.js").read_text().rstrip())
html = html.replace("__PHOTOS__", json.dumps(photos).replace("</", "<\\/"))
out = D / "Cresa_Austin_Office_Options_HR_Green.html"
out.write_text(html)
print(out.name, f"{out.stat().st_size/1e6:.1f} MB", len(photos), "photos")
