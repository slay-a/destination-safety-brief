# BiblioHook — iOS Book PDF Summaries + Topic Feed (RAG-backed)

BiblioHook is an iOS-first reading companion that lets users upload book PDFs, generate grounded summaries, and explore key topics in a scrollable feed with memorable (and optionally funny) explanations — while minimizing hallucinations via Retrieval-Augmented Generation (RAG) and citations.

## Why BiblioHook
Most “book summary” apps ship curated summaries. BiblioHook focuses on **your** documents:
- Upload a PDF (book, notes, course reader)
- Get **full summaries** and **topic-based summaries**
- Ask questions with **answers grounded in the PDF** (with citations)
- Browse a “topic feed” that turns book concepts into short, engaging cards

---

## Core Features

### PDF → Summaries
- Upload PDF → parse text (layout-aware where possible)
- Generate:
  - Full summary (short/medium/long)
  - Topic outline (auto-detected)
  - Topic-based summaries

### Ask Your Book (RAG + Citations)
- Semantic retrieval over embedded chunks (vector search)
- Model answers constrained to retrieved content
- Returns citations (page/chunk references where available)
- Refuses to answer when evidence is missing (“Not found in this book.”)

### Topic Feed (Scroll)
- Converts extracted topics into feed cards:
  - “Key idea” in 1–2 lines
  - Example/analogy
  - Optional “meme-style caption” **(text-only by default to avoid copyright issues)**

### Book Lookup (Optional add-on)
- Search by title/author/ISBN via public APIs (Google Books / Open Library)
- Save metadata into personal library

### Personalization
- Reading preferences: genres, tone (simple/technical/funny), summary length
- Per-user usage limits (free vs paid)

---

## Non-Goals (for MVP)
- No social feed / public sharing at launch
- No copyrighted meme images at launch (text-only captions or licensed assets only)
- No “guaranteed page-perfect citations” for every PDF (depends on PDF structure)

---

## Architecture (Industry Standard)

**High-level flow**
1. iOS uploads PDF → API stores file in object storage
2. API enqueues background ingestion job
3. Worker pipeline:
   - Parse PDF → structured text
   - Chunk → embed → store vectors
   - Generate topics + summaries + feed cards
4. iOS polls job status and fetches outputs
5. Chat/Q&A uses RAG retrieval + cited answers

**Why background jobs?**
PDF parsing + embedding + summarization are slow/expensive and must not block API requests.

---

## Tech Stack (Recommended)

### iOS
- SwiftUI (premium native UI, smooth feed)
- StoreKit 2 for subscriptions and offers

Apple: StoreKit APIs are the standard way to implement auto-renewable subscriptions.  
Source: Apple Developer docs. :contentReference[oaicite:0]{index=0}

### Backend
- FastAPI (Python) for API
- Background workers (Celery or RQ) + Redis
- Object storage (S3/R2/GCS) for PDFs

### Database + Vector Search (RAG)
- PostgreSQL (primary DB)
- pgvector extension for embeddings + similarity search

pgvector is an open-source Postgres extension for vector similarity search. :contentReference[oaicite:1]{index=1}

### LLM API
- OpenAI Responses API for generation (summaries, topics, feed cards, RAG answers)

OpenAI positions the Responses API as the unified interface for building these workflows. :contentReference[oaicite:2]{index=2}

---

## Hallucination Minimization Strategy (Must-Read)

BiblioHook is designed to be “grounded-first.”

### Rules enforced server-side
- The model must only use retrieved chunks as evidence for factual claims.
- Every key claim should include at least one citation.
- If evidence is missing → respond with “Not found in the provided document.”
- Summaries are generated via staged summarization (chunk → section → final), not one-shot.

### Output format
Responses are returned in structured JSON:
- `summary`
- `key_points[] { text, citations[] }`
- `topics[] { title, description, citations[] }`
- `limitations[]` (missing sections, unreadable pages, etc.)

---

## Monetization (Cost-Safe)

Because LLM usage costs money, BiblioHook uses a **hybrid** model:

### Free tier (hook)
- Limited uploads (ex: 1 active book)
- Limited pages per upload (ex: first 20–30 pages)
- Limited Q&A per day (ex: 5 questions/day)
- Limited feed cards per book

### Paid tier (subscription)
- Higher limits and faster processing
- More topic summaries and deeper Q&A

### Credits (optional)
- For power users: buy extra “processing credits” (pages or Q&A turns)

### Cost Controls (non-negotiable)
- Cache summaries/topics/feed per book + settings
- Token budgets per request
- Rate limiting and abuse protection
- Usage ledger in DB: every model call increments user usage

---

## Repository Layout (Suggested Monorepo)

