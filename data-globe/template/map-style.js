const T = {
  dark: {
    land: '#2B231D', ocean: '#100E0D', ice: '#322A24', urban: '#231D19', coast: 'rgba(255,170,110,.16)',
    border: 'rgba(255,235,220,.16)', road: 'rgba(255,220,190,.10)', country: 'rgba(255,235,220,.36)',
    ocean_t: 'rgba(255,214,186,.22)', city: 'rgba(255,235,220,.55)', halo: 'rgba(13,12,12,.85)',
  },
  bright: {
    land: '#D8CDBF', ocean: '#121010', ice: '#E9E3DA', urban: '#CBBFB0', coast: 'rgba(80,50,30,.25)',
    border: 'rgba(70,45,30,.35)', road: 'rgba(90,60,40,.22)', country: 'rgba(52,36,26,.62)',
    ocean_t: 'rgba(255,214,186,.24)', city: 'rgba(40,28,20,.75)', halo: 'rgba(225,215,203,.9)',
  },
};

export function landPalette(theme) { return T[theme]; }

export function globeStyle(theme = "dark") {
  const t = T[theme];
  const style = {
    version: 8,
    glyphs: 'https://tiles.openfreemap.org/fonts/{fontstack}/{range}.pbf',
    projection: { type: 'globe' },
    sources: {
      omt: { type: 'vector', url: 'https://tiles.openfreemap.org/planet', maxzoom: 6 },
      streets: { type: 'vector', url: 'https://tiles.openfreemap.org/planet', minzoom: 7 },
    },
    layers: [
      { id: 'land', type: 'background', paint: { 'background-color': t.land } },
      { id: 'ice', type: 'fill', source: 'omt', 'source-layer': 'landcover', filter: ['==', ['get', 'class'], 'ice'], paint: { 'fill-color': t.ice } },
      { id: 'urban', type: 'fill', source: 'omt', 'source-layer': 'landuse', minzoom: 7, filter: ['==', ['get', 'class'], 'residential'], paint: { 'fill-color': t.urban } },
      { id: 'water', type: 'fill', source: 'omt', 'source-layer': 'water', paint: { 'fill-color': t.ocean } },
      { id: 'coast', type: 'line', source: 'omt', 'source-layer': 'water', paint: { 'line-color': t.coast, 'line-width': ['interpolate', ['linear'], ['zoom'], 1, 0.5, 8, 1.1] } },
      { id: 'roads', type: 'line', source: 'omt', 'source-layer': 'transportation', minzoom: 7, filter: ['in', ['get', 'class'], ['literal', ['motorway', 'trunk', 'primary', 'secondary']]], paint: { 'line-color': t.road, 'line-width': ['interpolate', ['linear'], ['zoom'], 8, 0.5, 13, 2] } },
      { id: 'border', type: 'line', source: 'omt', 'source-layer': 'boundary', filter: ['all', ['==', ['get', 'admin_level'], 2], ['!=', ['get', 'maritime'], 1]], paint: { 'line-color': t.border, 'line-width': 0.7 } },
      { id: 'ocean-name', type: 'symbol', source: 'omt', 'source-layer': 'water_name', filter: ['==', ['get', 'class'], 'ocean'], layout: { 'text-field': ['get', 'name:en'], 'text-font': ['Noto Sans Italic'], 'text-size': 11, 'text-letter-spacing': 0.35, 'text-max-width': 6 }, paint: { 'text-color': t.ocean_t } },
      { id: 'country', type: 'symbol', source: 'omt', 'source-layer': 'place', filter: ['all', ['==', ['get', 'class'], 'country'], ['<=', ['get', 'rank'], 2]], maxzoom: 6, layout: { 'text-field': ['upcase', ['get', 'name:en']], 'text-font': ['Noto Sans Regular'], 'text-size': 10, 'text-letter-spacing': 0.26, 'text-max-width': 7 }, paint: { 'text-color': t.country } },
      { id: 'city-name', type: 'symbol', source: 'omt', 'source-layer': 'place', minzoom: 8, filter: ['in', ['get', 'class'], ['literal', ['city', 'town', 'suburb']]], layout: { 'text-field': ['get', 'name:en'], 'text-font': ['Noto Sans Regular'], 'text-size': 11.5, 'text-letter-spacing': 0.05 }, paint: { 'text-color': t.city, 'text-halo-color': t.halo, 'text-halo-width': 1.2 } },
    ],
  };
  // World coastlines are deliberately simplified. Never stretch their cached
  // polygons across a city while its street tiles are still arriving.
  style.layers = style.layers.flatMap((layer) => {
    if (layer.id === 'ice' || layer.id === 'water' || layer.id === 'coast') {
      return [{ ...layer, maxzoom: 7 }, { ...layer, id: `${layer.id}-streets`, source: 'streets', minzoom: 7 }];
    }
    if (['urban', 'roads', 'city-name'].includes(layer.id)) return [{ ...layer, source: 'streets' }];
    return [layer];
  });
  return style;
}
