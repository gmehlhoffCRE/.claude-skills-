import fs from 'fs';
import * as topojson from 'topojson-client';
import { geoAlbersUsa, geoPath } from 'd3-geo';
const us = JSON.parse(fs.readFileSync('node_modules/us-atlas/states-albers-10m.json'));
const states = topojson.feature(us, us.objects.states).features;
const neighbors = topojson.neighbors(us.objects.states.geometries);
const path = geoPath(null);
const proj = geoAlbersUsa().scale(1300).translate([487.5, 305]);
const out = { width: 975, height: 610, states: [], cities: {} };
states.forEach((f, i) => {
  const g = f.geometry;
  const polys = g.type === 'Polygon' ? [g.coordinates] : g.coordinates;
  out.states.push({ name: f.properties.name, id: f.id, rings: polys.map(p => p[0]), neighbors: neighbors[i],
                    centroid: path.centroid(f), area: path.area(f) });
});
const cities = JSON.parse(fs.readFileSync(process.argv[2]));
for (const [k, [lon, lat]] of Object.entries(cities)) out.cities[k] = proj([lon, lat]);
fs.writeFileSync('map.json', JSON.stringify(out));
console.log(out.states.length, 'states', Object.keys(out.cities).length, 'cities');
