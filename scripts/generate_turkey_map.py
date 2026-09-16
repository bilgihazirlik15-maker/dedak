"""Generate the local province map used by the accredited-programs dialog."""

from pathlib import Path
from urllib.request import urlopen
import json

ROOT = Path(__file__).resolve().parent.parent
# Province boundaries originate with OCHA/HDX COD-AB-TUR (CC BY-IGO).
# This pinned snapshot is distributed by ttezer/turkiye-harita-verisi.
PROVINCES = "https://raw.githubusercontent.com/ttezer/turkiye-harita-verisi/83eeb7a1e0a476dde81ada1a62f803231cf16e61/dist/geojson/provinces.geojson"
COUNTRIES = "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
WIDTH, HEIGHT = 1000, 460
LON_MIN, LON_MAX = 25.5, 45.5
LAT_MIN, LAT_MAX = 34.0, 43.0


def project(point):
    lon, lat = point
    return ((lon - LON_MIN) / (LON_MAX - LON_MIN) * WIDTH,
            (LAT_MAX - lat) / (LAT_MAX - LAT_MIN) * HEIGHT)


def distance_to_segment(point, start, end):
    dx, dy = end[0] - start[0], end[1] - start[1]
    if dx == dy == 0:
        return ((point[0] - start[0]) ** 2 + (point[1] - start[1]) ** 2) ** .5
    t = max(0, min(1, ((point[0] - start[0]) * dx + (point[1] - start[1]) * dy) / (dx * dx + dy * dy)))
    return ((point[0] - start[0] - t * dx) ** 2 + (point[1] - start[1] - t * dy) ** 2) ** .5


def simplify(points, tolerance=.6):
    if len(points) < 3:
        return points
    keep = {0, len(points) - 1}
    stack = [(0, len(points) - 1)]
    while stack:
        first, last = stack.pop()
        index = max(range(first + 1, last), key=lambda i: distance_to_segment(points[i], points[first], points[last]), default=None)
        if index is not None and distance_to_segment(points[index], points[first], points[last]) > tolerance:
            keep.add(index)
            stack.extend(((first, index), (index, last)))
    return [points[i] for i in sorted(keep)]


def path(geometry):
    polygons = geometry["coordinates"] if geometry["type"] == "MultiPolygon" else [geometry["coordinates"]]
    segments = []
    for polygon in polygons:
        for ring in polygon:
            points = simplify([project(point) for point in ring])
            if len(points) >= 3:
                segments.append("M" + "L".join(f"{x:.1f},{y:.1f}" for x, y in points) + "Z")
    return "".join(segments)


with urlopen(PROVINCES, timeout=45) as response:
    provinces = json.load(response)["features"]
with urlopen(COUNTRIES, timeout=45) as response:
    countries = json.load(response)["features"]

assert len(provinces) == 81
cyprus = next(feature for feature in countries if feature["properties"]["ADMIN"] == "Cyprus")
province_paths = "\n".join(f'<path d="{path(feature["geometry"])}"/>' for feature in provinces)
cyprus_path = path(cyprus["geometry"])

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" aria-hidden="true">
<!-- Province boundaries: OCHA/HDX COD-AB-TUR, CC BY-IGO, via {PROVINCES} -->
<!-- Cyprus coastline: Natural Earth public domain, {COUNTRIES} -->
<g fill="#73b3dc" stroke="#fff" stroke-width="1.15" stroke-linejoin="round">
{province_paths}
<path d="{cyprus_path}"/>
</g>
</svg>
'''
(ROOT / "assets/turkey-map.svg").write_text(svg, encoding="utf-8")
print("Generated assets/turkey-map.svg with 81 province boundaries")
