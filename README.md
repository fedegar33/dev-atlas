# DevAtlas

**Evidence-based technical knowledge explorer and reproducible RAG experiment lab.**

## What we're building
An application for exploring a curated library of technical EPUB books, asking questions with verifiable source references, and comparing RAG pipelines using real evaluation evidence. Initial subject matter: AI engineering, RAG, agents, and evaluation.

## Goals
- Learn RAG fundamentals deeply through controlled experiments, not feature accumulation.
- Preserve book/chapter/section provenance and code blocks where possible.
- Support grounded answers and source inspection.
- Show the history of retrieval improvements **and regressions**, including accuracy/latency/cost tradeoffs.
- Produce a credible technical portfolio demonstration.

## Initial scope
- **EPUB only**; one legally usable, fixed corpus snapshot for the baseline.
- **v1:** simple EPUB extraction → fixed-size chunking → embeddings → pgvector dense retrieval → minimal grounded QA.
- Evaluation dataset created **before or alongside** v1, starting with 15–30 human-reviewed questions and evidence references.
- Braintrust tracks experiments; `pytest` covers deterministic ingestion and scoring tests.
- Next.js UI can start minimal; a visual experiment comparison interface comes later.

## Not in v1
Docling, PDF/HTML ingestion, hybrid search, reranking, GraphRAG/Neo4j, a generic web crawler, complex agents, production-scale auth or multi-tenancy. These are possible later experiments, **not** prerequisites.

## Planned evolution (hypotheses, not promises)
| Stage | Change under test | Primary question |
|---|---|---|
| v1 | Naive EPUB + fixed chunks + dense retrieval | What is our baseline? |
| v2 | Docling-based extraction | Does better document structure help? |
| v3 | Structure-aware chunking | Does respecting sections improve evidence coverage? |
| v4 | PostgreSQL lexical + dense fusion | Does hybrid retrieval improve exact technical terms? |
| v5 | Reranking | Is better ordering worth the latency/cost? |
| v6+ | Query rewriting, parent-child, contextual retrieval, etc. | Which targeted technique addresses observed failures? |

Version numbers label **experiment configurations**, not independent codebases. Changes may be rejected or reordered based on results.

## Repository layout
```text
AGENTS.md
README.md
docs/
  ARCHITECTURE.md
  EVALUATION.md
  EXPERIMENTS.md
experiments/
  v1-baseline.yaml        # illustrative starter config
backend/
  pyproject.toml         # uv project, dependencies, Ruff and pytest configuration
  uv.lock                # resolved dependency versions
  src/
    api/                 # FastAPI boundary
    agent/               # agent execution, tools and system instructions
    rag/                 # parsing, chunking, indexing and retrieval
    evals/               # scorers and evaluation runners
  tests/                 # deterministic tests added with implementation
frontend/                # planned Next.js application; not scaffolded yet
```

## Python development
The backend uses Python 3.14, uv for dependency management, Ruff for linting and
formatting, and pytest for deterministic tests. From `backend/`:

```sh
uv sync --locked
uv run ruff check .
uv run ruff format --check .
```

Run `uv run pytest` for deterministic tests (no API key or network required).
The four packages live directly under `src/`
and are installed by uv, so imports do not require modifying `PYTHONPATH`.

Initial dependencies prepare FastAPI/Uvicorn, LangChain primitives via `langchain-core`,
Psycopg/pgvector, and Braintrust. PostgreSQL with the pgvector extension must be
provisioned separately when indexing is implemented. Provider-specific model
integrations beyond OpenAI, Docling, and the frontend remain deferred. Installing dependencies
does not configure external services or send corpus content to them. The full
`langchain` package currently pulls in LangGraph, so only `langchain-core` is
included to respect the MVP boundary.

## Minimal chat API
From `backend/`, copy `.env.example` to `.env` and set `OPENAI_API_KEY` locally.
The environment file is ignored by Git. Start the development server:

```sh
uv sync --locked
uv run --env-file .env uvicorn api.main:app --reload
```

Interactive API docs are available at http://127.0.0.1:8000/docs. Try:

```sh
curl http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Hola, ¿quién sos?"}'
```

`POST /chat` returns `{"reply":"..."}`. Each request is independent; there is no
history, streaming, tool loop, or RAG yet. The system prompt lives in
`backend/src/agent/prompts.py`. Messages must be nonblank strings of at most
8,000 characters. Invalid input returns 422; missing credentials or provider rate
limits return 503; provider timeouts return 504; other provider errors or empty
output return 502 without exposing upstream error details.

The agent uses `langchain-openai` with the Responses API, `store=False`, a
30-second timeout, no automatic retries, and a 1,024-token output limit. The
default is `gpt-5.6-terra` with reasoning disabled for this minimal interaction.
[OpenAI describes it as balancing intelligence and cost](https://developers.openai.com/api/docs/models/gpt-5.6-terra).
Override it with `OPENAI_MODEL` using a model supporting the same Responses API
parameters. This is a provisional choice, not a measured RAG result.
Live requests send the supplied message to OpenAI and incur API usage charges;
the automated tests use simulated models and HTTP responses.

## Learning references
- https://buildevals.com/ — primary learning guide for evaluation methodology.
- https://github.com/NirDiamant/RAG_Techniques — reference implementations and RAG techniques; review repository license before reuse.
- https://www.braintrust.dev/ — evaluation execution and experiment history.
- https://docling-project.github.io/docling/ — candidate document parser for a future iteration.

## Content rights
Public demos must use appropriately licensed or permitted source materials. Purchased Manning EPUBs are **private-only** and should not be committed, redistributed, or exposed in public eval traces. Processing rights depend on the license/terms applicable to each book.

## First implementation milestone
1. Choose one EPUB and record its license/source and SHA-256 checksum.
2. Write tests for extraction quality, section ordering, code preservation where applicable, and stable evidence identifiers.
3. Implement a simple EPUB extractor; save normalized source records.
4. Curate initial gold questions and source evidence references.
5. Add fixed-size chunks, embeddings, pgvector search, and baseline retrieval scorers.
6. Record the first Braintrust experiment and document failures.

**Do not begin v2 until v1 has a measured baseline.**
