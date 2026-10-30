# Fixed prompts and study evidence

Visitors choose an approach and provide structured study information. There is no system-prompt or user-prompt editor. Arbitrary prompt/model fields are rejected by the run API. Prompt previews are read-only.

`prompts/methods.json` retains the eight original representative templates and their original internal IDs. MIDUS generation still uses `spa/prompts.py` without changes. The public display mapping remains SPA7 = original M8 and SPA8 = original M7.

For a custom study, `spa/custom.py` fills the same template placeholders with the declared measures, records and output schema. A fixed server-owned system layer explicitly maps original cohort/wave/life-satisfaction wording to the declared population and predictor/outcome fields. It specifies raw item generation and local scoring. This is an adaptation, not an identical reproduction of the original evaluation.

`spa/evidence.py` appends a fixed system policy and JSON-encoded reviewed source text. Adding papers does not change the user prompt or method procedure. Source text is untrusted reference data, even though the controlled wrapper is delivered through system instructions. The policy rejects embedded instructions and preferred results; hypotheses are context rather than enforced findings. This reduces instruction-confusion risk and is not a guarantee of model compliance.

PDFs are parsed locally in function memory with pypdf, without an LLM extraction or summarization request. Full extracted text is shown before inclusion. Page markers identify PDF page positions; they may differ from printed page numbers. Empty pages are flagged, not silently interpreted. Citation links are not fetched. Review tables, symbols and extraction order. Scanned, protected, overlong or malformed PDFs receive guidance to paste selected excerpts instead. Limits are three sources, 60,000 source characters in total, 1.5 MB and 40 pages per PDF.

The full study context and evidence are included in the signed input digest. Changes after preparation invalidate the request. Downloads include supporting_information.json plus metadata identifying the adaptation and original method-bank checksum. Free numerical examples do not learn from papers; only AI generation uses the evidence. The application does not independently validate papers, measurement sources, claims or numerical findings.
