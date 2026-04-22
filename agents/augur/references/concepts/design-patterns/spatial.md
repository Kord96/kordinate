---
kind: concept
name: spatial
signatures: {}
source:
  memory_concept: memory/catalog/concepts/spatial.md
type: pattern
abstraction:
- data
- geospatial
scope: domain
status: primary
---

# Explanation

## Recognition

How to identify this pattern in code.

### Signatures

- `geometry`, `Point`, `Polygon`, `LineString` type definitions or column types
- `latitude`, `longitude`, `lat`, `lng`, `coordinates` fields on models
- GeoJSON structures: `type: "Feature"`, `geometry: { type: "Point", coordinates: [...] }`
- PostGIS functions: `ST_Distance`, `ST_Contains`, `ST_Within`, `ST_Intersects`, `ST_Buffer`
- `spatial_index`, `GIST` index, `rtree` index creation on geometry columns
- `geofence`, `bounding_box`, `bbox`, `envelope` boundary computations
- Python: `shapely`, `geopandas`, `pyproj`, `geopy` library imports
- JS/TS: `turf.js`, `mapbox-gl`, `leaflet`, `@types/geojson` imports
- Go: `orb`, `go-geom`, `tegola`, PostGIS via `pgx` with geometry types
- Rust: `geo`, `geozero`, `postgis` crate, `rtree` spatial index

### Confidence

- **high** -- PostGIS or spatial database with ST_ functions, spatial index, and GeoJSON serialization across API boundaries
- **medium** -- Shapely or turf.js geometry operations with coordinate reference system awareness
- **low** -- Raw latitude/longitude floats stored without geometry types or spatial query capability

## Architecture

### When to use
- Location-based services requiring proximity search, geofencing, or route computation
- Mapping and GIS applications with polygon operations and spatial joins
- Any domain where distance, containment, or intersection queries are core access patterns

### Anti-patterns
- Storing coordinates as separate float columns without a proper geometry type, losing spatial query capability
- Computing distances in application code instead of using database-level spatial functions with spatial indices
- Ignoring coordinate reference systems (CRS), leading to incorrect distance calculations across hemispheres

### Complements
- [search-index](/concepts/search-index) — spatial queries often combine with full-text search for location-aware results
- [cache-aside](/concepts/cache-aside) — geofence lookups benefit from caching for hot regions
- [pagination](/concepts/pagination) — spatial queries return bounded result sets requiring pagination

## Impact

Spatial data requires specialized indexing (R-tree, GiST) that differs fundamentally from B-tree indices. Query performance depends heavily on spatial index health, and incorrect CRS handling produces silently wrong results that are difficult to catch without geospatial-aware testing.

### Relationship To Other Concepts

- Related to [search-index](/concepts/search-index) because this concept commonly appears alongside it or is clarified by contrast with it.
- Related to [cache-aside](/concepts/cache-aside) because this concept commonly appears alongside it or is clarified by contrast with it.
- Related to [pagination](/concepts/pagination) because this concept commonly appears alongside it or is clarified by contrast with it.

### Boundary

Use `spatial` when the important observation is this specific architectural concern within a domain-modeling or product-domain concern.

Do not use it just because a few signatures match; the surrounding responsibilities and architectural role should line up too.
