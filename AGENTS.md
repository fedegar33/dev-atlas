# AGENTS.md — DevAtlas

## Mission
Build **DevAtlas**, an evidence-based technical-book research assistant and an **experimental RAG laboratory**. The primary deliverable is not merely a chatbot: it is a reproducible record of what improves or degrades retrieval and answer quality.

## Read first
1. `README.md` — product scope and milestones.
2. `docs/ARCHITECTURE.md` — system boundaries and data flow.
3. `docs/EVALUATION.md` — evaluation-first requirements.
4. `docs/EXPERIMENTS.md` — experiment lifecycle and reproducibility.

## Technology decisions
- Frontend: **Next.js + TypeScript**.
- Backend: **Python + FastAPI**.
- Orchestration: **LangChain**, kept thin; do not introduce LangGraph without a demonstrated need.
- Storage: **PostgreSQL + pgvector**; PostgreSQL full-text search for later hybrid retrieval.
- Evals and experiment tracking: **Braintrust**; `pytest` for deterministic tests; custom retrieval metrics where appropriate.
- Document format for MVP: **EPUB only**. Other formats are future possibilities, not MVP requirements.
- Parsing: **v1 naive EPUB extraction** as a baseline; **Docling** is a subsequent experiment, not a mandatory v1 dependency.
- Diagrams: **Archify** for authoring/presentation when available; keep a text-based, version-controlled description of the architecture as source of truth.
- No Neo4j, graph database, Redis, or complex agent framework in MVP.

## Working rules for coding agents
- Implement **one small, testable milestone at a time**. Do not build future milestones speculatively.
- Start changes by stating the hypothesis, expected impact, and evaluation plan. For simple bug fixes, a concise test plan suffices.
- Prefer **failing tests/evals first** when a testable requirement is known. Never fabricate a failing score or force tests to fail.
- Keep parsing, chunking, indexing, retrieval, reranking, generation, and evaluation **separate**.
- Retrieval variants are **compositions/configurations**, not copied `retrieval_v1.py`, `retrieval_v2.py`, etc.
- Keep baseline strategies available for comparison. Do not silently overwrite previous experiment configurations or datasets.
- Every result must be reproducible: capture config, Git commit, corpus snapshot/checksum, dataset version, model IDs, embedding dimension, index build ID, scorer version, and relevant parameters.
- Do not compare Recall@K against chunk IDs from incompatible chunking strategies. Prefer stable source sections/evidence spans, with a documented matching rule.
- Do not change the evaluation set to make a model look better. Separate development cases from held-out cases.
- Use deterministic metrics for retrieval when gold evidence is available; use LLM judges as supplemental, calibrated measurements, not unquestionable ground truth.
- Preserve source provenance and attribution throughout the pipeline. Answer citations must point to actual retrieved evidence.
- Keep private purchased EPUBs, extracted content, credentials, and user-specific datasets **out of Git and public deployments**. Respect licenses and avoid distributing book content without permission.
- Never log secrets or full private-book passages to external telemetry/eval services without explicit opt-in and appropriate controls.
- Avoid unnecessary abstraction and dependency growth. Explain tradeoffs briefly in PRs.
- Update docs when architecture, experiment methodology, or product scope changes.

## Definition of done for a RAG change
1. Automated tests pass.
2. The same frozen evaluation dataset was run against baseline and candidate (or the limitation is explained).
3. Per-case failures and regressions were inspected, not just aggregate averages.
4. Latency and, when applicable, token/API cost were recorded.
5. Config and experiment metadata were saved; findings summarized in `docs/EXPERIMENTS.md` or an experiment report.
6. Citations and source IDs remain traceable.

## Reference material (guidance, not code to copy blindly)
- Evals curriculum: https://buildevals.com/
- RAG technique examples: https://github.com/NirDiamant/RAG_Techniques
- Braintrust: https://www.braintrust.dev/
- Docling: https://docling-project.github.io/docling/

Check upstream licenses before reusing code, figures, or content. Treat examples as hypotheses to test on our corpus.
