# Destination Safety Brief (iOS + Backend)

An evidence-first iOS app that generates a **destination safety brief** using **legitimate, authoritative sources only**, where **every fact is traceable** to its origin.

**Product promise**
- We do **not** tell users where to go.
- We show **verified facts**, **recent official advisories**, and **clearly labeled user reviews** (shown as reviews, not recommendations).
- **Every claim is linked** to a source URL and quoted evidence span.

---

## What this app generates

A structured `DestinationSafetyBrief` report:

- **What is known** (facts from official sources)
- **What is uncertain** (missing data / “not found in provided sources”)
- **What changed recently** (deltas from prior snapshots)
- **What people report** (reviews, explicitly labeled user-generated)

No “safety score” or conclusions.

---

## Core sources (API/RSS first)

### Safety & health (authoritative)
- **U.S. Department of State**: Travel Advisories + Country Information (API/RSS)
- **CDC**: Travelers’ Health RSS + Travel Notices RSS
- **WHO**: Disease Outbreak News (and regional RSS feeds if needed)

### Place basics / mapping
- **GeoNames**: place metadata (CC BY attribution)
- **OpenStreetMap**: mapping + geocoding (respect attribution + usage limits; Nominatim policies apply)

### Reviews (licensed only)
- **Google Places** reviews only under Google policies + attribution requirements  
  Reviews are treated as **user-generated**, can be noisy, and are labeled as such.

### Scraping rule (only when allowed)
Only scrape pages that clearly allow it (robots + terms). Rate limit heavily, cache responses, and store:
- source URL
- fetch timestamp
- extracted evidence snippet(s)

---

## System architecture

### A) iOS app (SwiftUI)
- Destination search
- Safety overview dashboard
- Sources tab (every claim clickable → excerpt + link)
- Updates tab (what changed since last check)
- Save/share report as PDF

### B) Backend (all fetching happens here)
- **Fetcher service**: API/RSS + allowed scraping
- **Normalizer**: converts to a unified schema
- **Store**: Postgres + Redis cache
- **LLM report service**: generation + verification
- **Audit log**: stores source URLs, timestamps, and extracted snippets for every report

### C) LLM layer (grounded, not freeform)
1. **Retrieval**: collect relevant chunks from the store for the destination  
2. **Generate (strict JSON)**: model outputs JSON only, with citations per statement  
3. **Verify**: second pass checks every statement maps to evidence; otherwise drop or mark “not found”

---

## Data model

We standardize early on a single schema:
- Destination profile (description, region, language, emergency numbers)
- Advisory summary (level, summary, last updated, link)
- Health notices (CDC notices, vaccines, outbreaks, links)
- Local risks (scams, transport, laws/customs — only if sourced)
- Environment risks (weather, earthquakes, wildfire — source dependent)
- Reviews (aggregated ratings + excerpts + platform attribution)
- Sources (list of sources used + timestamps + evidence spans)

See: [`docs/schema.md`](docs/schema.md)

---

## “No hallucinations” prompting rule

System prompt (conceptually):
- Use **only provided source excerpts**
- If a fact is absent: write **"not found in provided sources"**
- Do **not** recommend anything
- Output **JSON only** matching the schema
- Every field must include:
  - `sources: [url]`
  - `evidence: ["quoted span…"]`

A validator rejects output missing sources for key fields.

---

## Build plan

### Phase 1 — MVP (country-level)
- Destination search + report generation for countries
- State Dept advisory + country info
- CDC Travel Notices RSS
- Report with citations + source viewer
- Shareable PDF

### Phase 2 — City-level detail
- GeoNames metadata + maps
- Licensed reviews (Google Places) with required attribution
- Updates tracking (snapshots + diffs)

### Phase 3 — Trust & compliance
- Claim→evidence verification hardening
- Rate limiting + caching
- Terms/robots compliance log
- Disclaimers (“not medical/legal advice”)

### Phase 4 — Monetization
- B2C subscription (saved reports, alerts)
- B2B dashboard/API (travel agencies, universities, corporate travel, study abroad)

---

## Repo layout

- `ios/` — SwiftUI app
- `backend/` — fetch/normalize/store/report services
- `docs/` — product brief, schema, sources, compliance
- `scripts/` — local dev scripts

---

## Contributing

PRs welcome. Please keep the product invariant:
- **facts-only**
- **every line traceable**
- **reviews labeled as user-generated**
- **no recommendations**

---

## Disclaimer

This product provides informational summaries of third-party sources.  
It does not provide medical or legal advice.
