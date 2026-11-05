# Evaluation strategy

## Principle: eval-driven development
Use the **BuildEvals** curriculum (https://buildevals.com/) as the primary learning reference. Start by writing expected behaviors and representative failures. A baseline is allowed to perform poorly; do not fabricate failure or chase perfect scores on a tiny dataset.

## Two testing layers
1. **Deterministic tests (`pytest`):** EPUB extraction invariants, ordering, no accidental empty content, stable IDs, chunk/source provenance, scorer correctness.
2. **Quality evaluations (Braintrust):** ranked retrieval and grounded answers, with frozen datasets and comparable experiment metadata.

## Initial dataset
- Start with 15–30 manually reviewed cases from one fixed EPUB.
- Include factual, conceptual, exact term/code, cross-section, and unanswerable questions. Multi-book questions only after adding more books.
- Each case should contain: `case_id`, `question`, `category`, `gold_evidence` (stable source anchors and ideally spans), `reference_answer` where appropriate, `answerable`, and reviewer notes.
- Keep **development** and **held-out** sets separate. Grow them over time; version each dataset and never silently edit historical snapshots.

## Retrieval metrics
- **Recall@K**: fraction of relevant gold evidence retrieved in top K, under a documented evidence-matching rule.
- **MRR**: reciprocal rank of the first relevant result, averaged across answerable cases.
- **nDCG@K**: ranking quality when relevance labels support graded or binary gains.
- **Precision@K**: optional, depends on completeness of relevance judgments.
- **Latency p50/p95** and resource/API cost.

**Critical:** chunk IDs are not stable ground truth across chunking changes. Match retrieval to canonical sections/spans; document whether scoring is at section or passage level. If a result covers only a small portion of a broad section, section-level Recall may overstate quality. Inspect both qualitative and quantitative evidence.

## Generation metrics (later)
- Groundedness/faithfulness and citation support.
- Answer correctness against reviewed references.
- Abstention on unanswerable questions.
- Latency, token use and cost.
- LLM-as-a-judge scorers may be useful, but validate with hand-labeled examples and record judge model/prompt versions. Do not treat vendor metric names as guarantees of validity.

## Minimum experiment protocol
1. State hypothesis and target failure cases.
2. Freeze corpus, evaluation dataset, and scoring logic.
3. Run baseline and candidate with the same evaluation conditions.
4. Compare aggregate scores **and per-case regressions**.
5. Record model versions, seed/temperature where relevant, run metadata and costs.
6. Write a short conclusion: keep, reject, or investigate.

## Braintrust usage
Use Braintrust for datasets, experiment runs, metadata, scorer results and side-by-side comparisons. Implement deterministic Recall@K/MRR/nDCG scorers ourselves when gold labels permit; optionally use built-in/Autoevals judge scorers for generation. Confirm current scorer APIs when implementing.

## Data privacy
Use only licensed/permitted public excerpts in public evaluation traces. Purchased EPUBs may be processed privately subject to terms, but never upload their full text or substantial passages to third-party eval logs by default.
