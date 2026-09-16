"""Create the local map asset from Natural Earth public-domain country outlines."""

from pathlib import Path
from urllib.request import urlopen
import json

ROOT = Path(__file__).resolve().parent.parent
SOURCE = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
WIDTH, HEIGHT = 1000, 460
LON_MIN, LON_MAX = 25.5, 45.5
LAT_MIN, LAT_MAX = 34.0, 43.0


def project(point):
    lon, lat = point
    return ((lon - LON_MIN) / (LON_MAX - LON_MIN) * WIDTH,
            (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * HEIGHT)


def outline(geometry):
    polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    segments = []
    for polygon in polygons:
        for ring in polygon:
            points = [project(point) for point in ring]
            segments.append("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points) + " Z")
    return " ".join(segments)


with urlopen(SOURCE, timeout=30) as response:
    features = json.load(response)["features"]

shapes = {feature["properties"]["ADMIN"]: outline(feature["geometry"])
          for feature in features if feature["properties"]["ADMIN"] in {"Turkey", "Cyprus"}}
assert set(shapes) == {"Turkey", "Cyprus"}

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" aria-hidden="true">
<!-- Coastlines: Natural Earth 1:110m Admin 0 countries, public domain. {SOURCE} -->
<defs>
  <linearGradient id="sea" x2="0" y2="1"><stop stop-color="#d8effb"/><stop offset="1" stop-color="#b8dcee"/></linearGradient>
  <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse"><path d="M50 0H0V50" fill="none" stroke="#ffffff" stroke-opacity=".28"/></pattern>
  <filter id="shadow" x="-10%" y="-15%" width="120%" height="130%"><feDropShadow dx="0" dy="4" stdDeviation="7" flood-color="#17426c" flood-opacity=".16"/></filter>
</defs>
<rect width="{WIDTH}" height="{HEIGHT}" rx="18" fill="url(#sea)"/>
<rect width="{WIDTH}" height="{HEIGHT}" rx="18" fill="url(#grid)"/>
<path d="{shapes['Turkey']}" fill="#f8fbff" stroke="#276394" stroke-width="2.4" stroke-linejoin="round" filter="url(#shadow)"/>
<path d="{shapes['Cyprus']}" fill="#f8fbff" stroke="#276394" stroke-width="2.4" stroke-linejoin="round" filter="url(#shadow)"/>
<text x="555" y="215" fill="#9ec3dc" font-family="Arial,sans-serif" font-size="44" font-weight="700" letter-spacing="8">TÜRKİYE</text>
</svg>
'''
(ROOT / "assets/turkey-map.svg").write_text(svg, encoding="utf-8")
print("Generated assets/turkey-map.svg")
