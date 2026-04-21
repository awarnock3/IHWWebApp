# IHW Archive REST API Design

**Status:** Design Phase  
**Version:** 1.0 (draft)  
**Framework:** Django REST Framework

## Overview

RESTful API to provide programmatic access to the International Halley Watch archive database. Enables automated data analysis, external visualizations, mobile apps, and third-party integrations.

## Base URL

```
https://ihw-archive.example.org/api/v1/
```

## Authentication

**Phase 1 (MVP):** Read-only, no authentication required  
**Phase 2:** Optional API key for rate limit increases  
**Phase 3:** OAuth2 for write operations (if needed)

## Rate Limiting

- **Unauthenticated:** 100 requests/hour
- **Authenticated:** 1000 requests/hour
- Headers returned: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Common Parameters

All list endpoints support:

| Parameter | Type | Description |
|-----------|------|-------------|
| `limit` | integer | Results per page (default: 50, max: 100) |
| `offset` | integer | Skip N results (for pagination) |
| `ordering` | string | Sort field, prefix with `-` for descending (e.g., `-date`) |
| `fields` | string | Comma-separated field list to limit response size |
| `expand` | string | Comma-separated relations to include (e.g., `metadata,ephemeris`) |

## Endpoints

### Observations

#### List/Search Observations

```http
GET /api/v1/observations/
```

**Query Parameters:**

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `start_date` | ISO 8601 | Observations on or after this date | `1985-12-01` |
| `end_date` | ISO 8601 | Observations on or before this date | `1986-01-15` |
| `network` | string | Filter by network code | `AMSN` |
| `subnet` | string | Filter by subnet code | `AMV` |
| `observer` | string | Filter by observer name (partial match) | `Smith` |
| `min_distance` | float | Minimum solar distance (AU) | `0.5` |
| `max_distance` | float | Maximum solar distance (AU) | `2.0` |
| `has_metadata` | boolean | Only observations with metadata | `true` |
| `has_files` | boolean | Only observations with files | `true` |

**Example Request:**

```bash
curl "https://ihw-archive.example.org/api/v1/observations/?start_date=1985-12-01&end_date=1985-12-31&network=AMSN&limit=10"
```

**Example Response:**

```json
{
  "count": 1247,
  "next": "https://ihw-archive.example.org/api/v1/observations/?offset=10&limit=10&start_date=1985-12-01&end_date=1985-12-31&network=AMSN",
  "previous": null,
  "results": [
    {
      "id": 324005,
      "date": "1985-12-07T00:00:00Z",
      "network": "AMSN",
      "network_name": "Amateur Studies Network",
      "subnet": "AMV",
      "subnet_name": "AMSN Visual Observations",
      "observer": "John Doe",
      "files_count": 2,
      "has_metadata": true,
      "solar_distance": 1.234,
      "links": {
        "self": "https://ihw-archive.example.org/api/v1/observations/324005/",
        "metadata": "https://ihw-archive.example.org/api/v1/observations/324005/metadata/",
        "ephemeris": "https://ihw-archive.example.org/api/v1/observations/324005/ephemeris/",
        "files": "https://ihw-archive.example.org/api/v1/observations/324005/files/",
        "web": "https://ihw-archive.example.org/search/observation/324005/"
      }
    }
  ]
}
```

#### Get Observation Detail

```http
GET /api/v1/observations/{id}/
```

**Example Request:**

```bash
curl "https://ihw-archive.example.org/api/v1/observations/324005/"
```

**Example Response:**

```json
{
  "id": 324005,
  "date": "1985-12-07T00:00:00Z",
  "network": "AMSN",
  "network_name": "Amateur Studies Network",
  "subnet": "AMV",
  "subnet_name": "AMSN Visual Observations",
  "discipline": 9,
  "discipline_name": "Amateur Studies",
  "observer": "John Doe",
  "observatory_id": 1234,
  "files_count": 2,
  "has_metadata": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z",
  "ephemeris": {
    "date": "1985-12-07T00:00:00Z",
    "heliocentric_distance": 1.234,
    "geocentric_distance": 1.456,
    "phase_angle": 45.6,
    "ra": 123.456,
    "dec": -12.345
  },
  "links": {
    "self": "https://ihw-archive.example.org/api/v1/observations/324005/",
    "metadata": "https://ihw-archive.example.org/api/v1/observations/324005/metadata/",
    "ephemeris": "https://ihw-archive.example.org/api/v1/observations/324005/ephemeris/",
    "files": "https://ihw-archive.example.org/api/v1/observations/324005/files/",
    "observatory": "https://ihw-archive.example.org/api/v1/observatories/1234/",
    "web": "https://ihw-archive.example.org/search/observation/324005/"
  }
}
```

#### Get Observation Metadata

```http
GET /api/v1/observations/{id}/metadata/
```

Returns discipline-specific metadata from the appropriate `idx_meta_*` table.

**Example Response:**

```json
{
  "observation_id": 324005,
  "table": "idx_meta_amvis",
  "fields": {
    "magnitude": 5.2,
    "magnitude_system": "visual",
    "focal_length": 1200.0,
    "aperture": 200.0,
    "coma_diameter": 15.0,
    "tail_length": 8.5,
    "tail_pa": 270.0,
    "quality": "good",
    "conditions": "clear",
    "seeing": 2.5
  },
  "links": {
    "observation": "https://ihw-archive.example.org/api/v1/observations/324005/"
  }
}
```

#### Get Observation Ephemeris

```http
GET /api/v1/observations/{id}/ephemeris/
```

Returns ephemeris data for the observation date.

**Example Response:**

```json
{
  "observation_id": 324005,
  "date": "1985-12-07T00:00:00Z",
  "heliocentric_distance": 1.234,
  "heliocentric_distance_unit": "AU",
  "geocentric_distance": 1.456,
  "geocentric_distance_unit": "AU",
  "phase_angle": 45.6,
  "phase_angle_unit": "degrees",
  "ra": 123.456,
  "ra_unit": "degrees",
  "dec": -12.345,
  "dec_unit": "degrees",
  "ecliptic_lon": 180.5,
  "ecliptic_lat": -2.3,
  "sun_distance": 1.234,
  "links": {
    "observation": "https://ihw-archive.example.org/api/v1/observations/324005/"
  }
}
```

#### Get Observation Files

```http
GET /api/v1/observations/{id}/files/
```

Lists all associated archive files.

**Example Response:**

```json
{
  "observation_id": 324005,
  "files": [
    {
      "id": 456789,
      "filename": "amv03239.fit",
      "type": "data",
      "size_bytes": 2764800,
      "path": "ihw-c-amvis-2-rdr-halley-v1.0/data/1985/12/07/amv03239.fit",
      "has_fits_header": true,
      "has_pds_label": true,
      "links": {
        "fits_header": "https://ihw-archive.example.org/api/v1/observations/324005/fits-header/",
        "pds_label": "https://ihw-archive.example.org/api/v1/observations/324005/pds-label/",
        "download": "https://ihw-archive.example.org/api/v1/files/456789/download/"
      }
    },
    {
      "id": 456790,
      "filename": "amv03239.lbl",
      "type": "label",
      "size_bytes": 1024,
      "path": "ihw-c-amvis-2-rdr-halley-v1.0/data/1985/12/07/amv03239.lbl",
      "has_fits_header": false,
      "has_pds_label": true,
      "links": {
        "pds_label": "https://ihw-archive.example.org/api/v1/observations/324005/pds-label/",
        "download": "https://ihw-archive.example.org/api/v1/files/456790/download/"
      }
    }
  ]
}
```

#### Get FITS Header

```http
GET /api/v1/observations/{id}/fits-header/
```

**Response Formats:**
- Default: `application/json` - Parsed FITS header as JSON
- `Accept: text/plain` - Raw 80-character FITS cards

**Example Response (JSON):**

```json
{
  "observation_id": 324005,
  "file": "amv03239.fit",
  "header": {
    "SIMPLE": true,
    "BITPIX": 16,
    "NAXIS": 2,
    "NAXIS1": 512,
    "NAXIS2": 512,
    "DATE-OBS": "1985-12-07T00:00:00",
    "OBSERVER": "John Doe",
    "TELESCOP": "200mm Schmidt-Cassegrain",
    "INSTRUME": "CCD Camera",
    "FILTER": "Clear",
    "EXPTIME": 300.0
  },
  "cards_count": 45,
  "blocks_count": 1
}
```

**Example Response (text/plain):**

```
SIMPLE  =                    T / file does conform to FITS standard             
BITPIX  =                   16 / number of bits per data pixel                  
NAXIS   =                    2 / number of data axes                            
NAXIS1  =                  512 / length of data axis 1                          
NAXIS2  =                  512 / length of data axis 2                          
...
END                                                                             
```

#### Get PDS Label

```http
GET /api/v1/observations/{id}/pds-label/
```

**Response Formats:**
- Default: `application/json` - Parsed PDS label as JSON
- `Accept: text/plain` - Raw PDS label text

**Example Response (JSON):**

```json
{
  "observation_id": 324005,
  "file": "amv03239.lbl",
  "label": {
    "PDS_VERSION_ID": "PDS3",
    "RECORD_TYPE": "FIXED_LENGTH",
    "RECORD_BYTES": 2880,
    "FILE_RECORDS": 960,
    "LABEL_RECORDS": 1,
    "DATA_SET_ID": "IHW-C-AMVIS-2-RDR-HALLEY-V1.0",
    "PRODUCT_ID": "AMV03239",
    "INSTRUMENT_HOST_NAME": "AMATEUR TELESCOPE",
    "INSTRUMENT_NAME": "VISUAL OBSERVER",
    "TARGET_NAME": "HALLEY",
    "START_TIME": "1985-12-07T00:00:00.000Z"
  }
}
```

### Networks & Subnets

#### List Networks

```http
GET /api/v1/networks/
```

**Example Response:**

```json
{
  "count": 9,
  "results": [
    {
      "id": 9,
      "code": "AMSN",
      "name": "Amateur Studies Network",
      "description": "Amateur observers worldwide contributed visual observations, drawings, and photographs",
      "subnet_count": 4,
      "observation_count": 12543,
      "links": {
        "subnets": "https://ihw-archive.example.org/api/v1/subnets/?network=AMSN",
        "observations": "https://ihw-archive.example.org/api/v1/observations/?network=AMSN"
      }
    }
  ]
}
```

#### List Subnets

```http
GET /api/v1/subnets/
```

**Query Parameters:**
- `network` - Filter by network code

**Example Response:**

```json
{
  "count": 24,
  "results": [
    {
      "code": "AMV",
      "name": "AMSN Visual Observations",
      "network": "AMSN",
      "network_name": "Amateur Studies Network",
      "discipline": 9,
      "has_metadata_table": true,
      "metadata_table": "idx_meta_amvis",
      "observation_count": 5432,
      "links": {
        "network": "https://ihw-archive.example.org/api/v1/networks/AMSN/",
        "observations": "https://ihw-archive.example.org/api/v1/observations/?subnet=AMV"
      }
    }
  ]
}
```

### Observatories

#### List Observatories

```http
GET /api/v1/observatories/
```

**Query Parameters:**
- `search` - Search name, location, code

**Example Response:**

```json
{
  "count": 234,
  "results": [
    {
      "id": 1234,
      "code": "OBS001",
      "name": "Mount Wilson Observatory",
      "location": "California, USA",
      "latitude": 34.2242,
      "longitude": -118.0572,
      "elevation": 1742.0,
      "observation_count": 156,
      "links": {
        "observations": "https://ihw-archive.example.org/api/v1/observations/?observatory=1234"
      }
    }
  ]
}
```

#### Get Observatory Detail

```http
GET /api/v1/observatories/{id}/
```

### Observers

#### List Observers

```http
GET /api/v1/observers/
```

**Query Parameters:**
- `search` - Search observer name

**Example Response:**

```json
{
  "count": 1234,
  "results": [
    {
      "name": "John Doe",
      "observation_count": 45,
      "networks": ["AMSN", "PPSN"],
      "date_range": {
        "first": "1985-11-15",
        "last": "1986-04-20"
      },
      "links": {
        "observations": "https://ihw-archive.example.org/api/v1/observations/?observer=John+Doe"
      }
    }
  ]
}
```

### Ephemeris

#### Query Ephemeris

```http
GET /api/v1/ephemeris/
```

**Query Parameters:**
- `start_date` - ISO 8601 date
- `end_date` - ISO 8601 date

**Example Response:**

```json
{
  "count": 365,
  "results": [
    {
      "date": "1985-12-07T00:00:00Z",
      "heliocentric_distance": 1.234,
      "geocentric_distance": 1.456,
      "phase_angle": 45.6,
      "ra": 123.456,
      "dec": -12.345,
      "ecliptic_lon": 180.5,
      "ecliptic_lat": -2.3
    }
  ]
}
```

#### Get Single Date Ephemeris

```http
GET /api/v1/ephemeris/{date}/
```

Where `{date}` is ISO 8601 format (e.g., `1985-12-07`).

### Statistics

#### Overall Statistics

```http
GET /api/v1/stats/summary/
```

**Example Response:**

```json
{
  "total_observations": 69094,
  "total_files": 125000,
  "networks": 9,
  "subnets": 24,
  "observers": 1234,
  "observatories": 234,
  "date_range": {
    "first": "1985-09-06",
    "last": "1989-05-03"
  },
  "perihelion_date": "1986-02-09",
  "peak_observation_date": "1986-03-15",
  "observations_by_network": {
    "AMSN": 12543,
    "LSPN": 8234,
    "PPSN": 15234
  }
}
```

#### Statistics by Network

```http
GET /api/v1/stats/by-network/
```

**Example Response:**

```json
{
  "networks": [
    {
      "code": "AMSN",
      "name": "Amateur Studies Network",
      "observation_count": 12543,
      "file_count": 23456,
      "observer_count": 456,
      "date_range": {
        "first": "1985-10-01",
        "last": "1988-12-31"
      }
    }
  ]
}
```

#### Timeline Statistics

```http
GET /api/v1/stats/by-date/
```

**Query Parameters:**
- `interval` - `day`, `week`, `month` (default: `month`)
- `start_date` - Optional start date
- `end_date` - Optional end date

**Example Response:**

```json
{
  "interval": "month",
  "data": [
    {
      "date": "1985-12-01",
      "observation_count": 1247,
      "networks_active": 5
    },
    {
      "date": "1986-01-01",
      "observation_count": 2345,
      "networks_active": 8
    }
  ]
}
```

## Error Responses

All errors follow consistent format:

```json
{
  "error": {
    "code": "not_found",
    "message": "Observation with ID 999999 not found",
    "status": 404
  }
}
```

**Common Error Codes:**

| HTTP Status | Code | Description |
|-------------|------|-------------|
| 400 | `invalid_parameter` | Invalid query parameter value |
| 401 | `authentication_required` | API key required |
| 403 | `rate_limit_exceeded` | Too many requests |
| 404 | `not_found` | Resource not found |
| 500 | `internal_error` | Server error |
| 503 | `archive_unavailable` | Archive files not available |

## Response Headers

All responses include:

```
Content-Type: application/json; charset=utf-8
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1609459200
X-API-Version: 1.0
```

## CORS

API supports CORS for browser-based clients:

```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
```

## Versioning

API version included in URL (`/api/v1/`). Breaking changes will increment version number.

## Client Examples

### Python (requests)

```python
import requests

# Search observations
response = requests.get(
    'https://ihw-archive.example.org/api/v1/observations/',
    params={
        'start_date': '1985-12-01',
        'end_date': '1985-12-31',
        'network': 'AMSN',
        'limit': 10
    }
)
observations = response.json()

# Get specific observation
obs_id = observations['results'][0]['id']
detail = requests.get(
    f'https://ihw-archive.example.org/api/v1/observations/{obs_id}/'
).json()

# Get metadata
metadata = requests.get(
    f'https://ihw-archive.example.org/api/v1/observations/{obs_id}/metadata/'
).json()
```

### JavaScript (fetch)

```javascript
// Search observations
const response = await fetch(
  'https://ihw-archive.example.org/api/v1/observations/?start_date=1985-12-01&network=AMSN'
);
const data = await response.json();

// Get metadata
const obsId = data.results[0].id;
const metadata = await fetch(
  `https://ihw-archive.example.org/api/v1/observations/${obsId}/metadata/`
).then(r => r.json());
```

### curl

```bash
# Search observations
curl "https://ihw-archive.example.org/api/v1/observations/?start_date=1985-12-01&network=AMSN&limit=5"

# Get observation detail with expanded relations
curl "https://ihw-archive.example.org/api/v1/observations/324005/?expand=metadata,ephemeris"

# Get FITS header as raw text
curl -H "Accept: text/plain" \
  "https://ihw-archive.example.org/api/v1/observations/324005/fits-header/"

# Rate limit check
curl -I "https://ihw-archive.example.org/api/v1/observations/"
```

## Implementation Roadmap

### Phase 1: Core API (MVP)
- [ ] Install Django REST Framework
- [ ] Create serializers for core models
- [ ] Implement observation endpoints (list, detail, metadata)
- [ ] Add filtering and pagination
- [ ] Basic error handling
- [ ] CORS configuration

### Phase 2: Extended Features
- [ ] Network/subnet/observatory endpoints
- [ ] Ephemeris endpoints
- [ ] Statistics endpoints
- [ ] FITS/PDS parsing endpoints
- [ ] Field selection (`?fields=`)
- [ ] Relation expansion (`?expand=`)

### Phase 3: Advanced Features
- [ ] Authentication (API keys)
- [ ] Rate limiting
- [ ] OpenAPI/Swagger documentation
- [ ] Response caching
- [ ] ETags support
- [ ] Bulk export formats (CSV)

### Phase 4: Performance & Monitoring
- [ ] Query optimization
- [ ] Database indexing
- [ ] API usage analytics
- [ ] Performance monitoring
- [ ] Error tracking

## Notes

- All timestamps in UTC
- Distances in Astronomical Units (AU) unless noted
- Angles in degrees unless noted
- API is read-only (no POST/PUT/DELETE operations)
- Archive file downloads require archive to be mounted
- Database-only mode: All metadata endpoints work without archive files
