# Experiment log and conventions

## Why configs, not eight retrieval modules?
A 'version' is a **named configuration** of parsing, chunking, embedding, retrieval, fusion and reranking. Implement strategies as reusable components. Preserve immutable configuration snapshots so historical comparisons are meaningful.

## Experiment record template
Copy this block for each meaningful experiment or keep a separate `experiments/reports/<id>.md` once the log grows.

```markdown
## EXP-001 — v1 naive dense baseline
Status: planned | running | complete | rejected
Hypothesis: A simple fixed-chunk dense retriever establishes a measurable baseline.
Change vs control: none (first baseline).
Corpus: <book + source checksum>
Dataset: <dataset name + immutable version>
Index build: <index_build_id>
Git commit: <sha>
Models: <embedding / generation / judge versions>
Config: experiments/v1-baseline.yaml
Braintrust run: <link or ID>
Scores: Recall@5=?, MRR=?, nDCG@5=?, latency p50/p95=?
Failure analysis: <specific case IDs and causes>
Decision: <retain baseline / investigate>
Next hypothesis: <one measurable change>
```

## Comparison rules
- One major change per controlled comparison whenever practical.
- Do not imply a cumulative v5 improvement was caused solely by the last feature.
- Keep a stable baseline and run ablations (e.g., fixed+hybrid vs hierarchical+dense) when attributing effects.
- Save failed experiments; negative results are valuable.
- Indexes are derived artifacts: rebuild using pinned config if not stored. If exact reconstruction is impossible, mark the experiment non-reproducible.
- Treat improvements as provisional with small datasets; report sample size and case-level differences.

## Planned experiments (not results)
| ID | Candidate | Hypothesis | Status |
|---|---|---|---|
| EXP-001 | v1 naive + fixed + dense | Establish baseline | Planned |
| EXP-002 | v2 Docling + fixed + dense | Parsing quality improves retrieval | Backlog |
| EXP-003 | v3 Docling + hierarchical + dense | Structure-aware chunks help | Backlog |
| EXP-004 | v4 Docling + hierarchical + hybrid | Lexical fusion helps exact terms | Backlog |
| EXP-005 | v5 + reranker | Ranking improves at acceptable latency | Backlog |

These are proposals, not predetermined successes. Rename or skip versions if evidence suggests another direction.
