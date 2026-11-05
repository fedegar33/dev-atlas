# Architecture — living design

## Logical pipeline
```text
EPUB (private or licensed corpus)
  → Parser [naive v1 | Docling later]
  → Normalized document + stable source references
  → Chunking strategy [fixed v1 | hierarchical later]
  → Embedding model
  → PostgreSQL + pgvector (versioned index builds)
  → Retriever [dense v1 | hybrid/rerank later]
  → LangChain orchestration + LLM
  → Answer + citations + retrieval trace
                 ↘ Braintrust eval runs

Next.js UI ↔ FastAPI API
```

## Responsibilities
### Current implementation
`POST /chat` in `api.main` validates a single message and calls `agent.chat`.
The agent sends a system instruction and user message through LangChain's
`ChatOpenAI` integration to OpenAI Responses and returns text. Model selection
uses `OPENAI_MODEL` (default `gpt-5.6-terra`); credentials use `OPENAI_API_KEY`.
This is a stateless connectivity milestone: no retrieval, tools, or corpus access
is implemented yet. The logical RAG pipeline above remains the target design.

### Package boundaries
Code lives in `backend/src/`, with four directly importable packages:
`api` for HTTP endpoints, `agent` for agent execution/tools/system instructions,
`rag` for the independent parsing/chunking/indexing/retrieval pipeline, and
`evals` for scorers and evaluation runners. Agent tools may call RAG components;
RAG components must remain usable without the agent. Experiment configurations
remain in the repository-level `experiments/` directory.

- **Parser:** convert EPUB into text/blocks, metadata, reading order and source locations; must not decide retrieval ranking.
- **Normalized source:** book ID, chapter/section identity, text/code blocks, provenance, parser version. A stable logical evidence anchor should survive chunking changes when feasible.
- **Chunker:** creates retrieval units from normalized source; chunks are derived artifacts and may change between experiments.
- **Index builder:** persists chunk sets and embeddings under an `index_build_id`; don't mix incompatible embedding models or chunk versions.
- **Retriever:** returns ranked evidence records with source anchors, scores, strategy and index version.
- **Generator:** uses only provided evidence to produce an answer with citations; handle insufficient evidence explicitly.
- **Evaluator:** measures retrieval and generation separately; runs the same frozen dataset against candidates.

## Data entities (conceptual, not a migration spec)
- `books`: identity, title, author, source rights, checksum.
- `source_documents`: book, parser version, normalized structure or artifact path.
- `source_sections`: stable source anchors and ordered content.
- `index_builds`: corpus checksum, parser/chunker/embedding config, build timestamp.
- `chunks`: index build, content, source section/span anchors, metadata.
- `embeddings`: chunk + model identifier + vector.
- `eval_cases` and `eval_runs`: dataset versions and experiment references (Braintrust may be the primary run store).

## Future formats
Keep a small `DocumentParser` boundary and normalized output contract. Do **not** implement PDF/HTML parsers, factories or a plugin system until there is a real requirement.

## Diagram workflow
Use Archify to create polished diagrams when needed. Keep this text diagram and architectural decisions in Git so the design remains inspectable even without Archify. Export diagram assets only when useful, and note the source/editable location.

## Decisions to revisit
- Exact normalized document schema and source-span anchoring.
- Embedding provider/model and data egress policy.
- How to serialize parsed documents (PostgreSQL JSONB vs local/object artifacts).
- Whether LangChain wrappers simplify or obscure experiment instrumentation.
