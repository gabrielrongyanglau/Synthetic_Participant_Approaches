# Verification

The original scientific engine was independently compared with all 8,000 final datasets and the full eligible human reference of 2,709 participants. All 6,374 mapped workbook cells passed, including 5,935 numerical values and 439 p-value display strings or significance decisions. The maximum absolute numerical difference was approximately 3.35 × 10⁻¹³. The historical per-tab checks are retained in `verification/validation_summary.csv`.

The original MIDUS study definition, representative prompt bank, sampling helpers, statistical formulas and source aggregate files are unchanged. Approaches are numbered SPA1–SPA8 as in the revised proposal. The source prompt bank and result files keep the original numbering and are byte-identical; `spa/numbering.py` relabels them on load, and a test confirms that SPA8 carries the proposal's reported values (SMD 0.0802; correlation MAE .1927 and .2445) and SPA7 its own (0.5822; .6574 and .7114).

## Current checks

The suite covers all original input methods, sample sizes, fixed-value preservation, missing values, numerical precision, duplication flags, statistical formulas, intervals, pairwise comparisons, exports and public background-response lifecycle. Provider requests are mocked; tests make no paid calls. The original-study chart payload is checked against the full-precision sources, including all 16 method/wave scatterplot combinations.

Additional tests cover custom questionnaire validation, reverse coding, complete-item mean/sum scoring, all eight custom generation procedures, matching templates, fixed predictor precision, pilot summary separation, server routes, score-only and mixed item/score human references, zero errors for identical references, suppression of uninformative two-coefficient pattern r, public method mapping and signed custom background responses. Altered context data are rejected before retrieval.

Python compilation and JavaScript syntax are checked. The browser ZIP writer is independently checked with Python's ZIP reader. Archive checks exclude credentials, caches, virtual environments and private participant data. `verification/build_checks.json` records the build settings and the SHA-256 hashes of the preserved scientific core files; run `python -m pytest -q` to reproduce the current test result.

Browser QA uses private static fixtures produced by the real API test client. It checks custom study setup, complete pilot recommendations, progression to generation, a 100-person fictional dataset, updated study chart labels and the SPA8 relationship advantage. This is frontend QA, not a live provider or Vercel deployment test. Preview fixtures are not distributed.

## Limits

Custom item-level generation is a new functional extension. Computational tests establish implementation behavior, not empirical fidelity for new measures, populations or outcomes. Sources and questionnaire validity require human verification. Hypothesis testing, causal claims, individual prediction, imputations and effect-size assumptions for power calculations need separate evidence.

No paid OpenAI call, live Vercel deployment test or independent security audit was performed. The owner should check a small fictional production run using the configured key. Provider retention rules apply despite temporary application processing. Durable recovery and exactly-once submission are not claimed.

## Research-funded trial and codebooks

The public interface and request schema now limit simulations to one approach, one dataset and 100 participants. Tests reject larger or repeated runs before provider access, including submissions using an older larger signed plan. Historical offline engines and original study results are unchanged.

Dataset responses provide a column-matched codebook for MIDUS and custom studies. Checks cover all exported columns, the four example MIDUS codes raised during review, generated-versus-fixed provenance, custom items and composite scoring, demographic inclusion and UTF-8 codebook CSV parsing. New tests cover optional contact/estimate settings and sanitized budget-related provider errors without automatic retries. Browser QA checks the visible planning estimate, funding notice, disabled larger samples/repetitions, single approach selection, dataset/codebook download controls and demographic fields.

The interface states that generation time varies from a few minutes to up to an hour depending on the complexity of the data generated. This is a planning estimate, not a measured performance result.

## Version 4.6.1: wording

Interface text, error messages, the variable guide and the codebook were reworded into plain statements without em dashes or semicolons. A browser scan of every visible page and a scan of the generated variable guide and codebooks found none of the listed patterns. Two preserved files, `spa/study.py` and `spa/workflow.py`, changed in message strings only, and their hashes are updated. The study configuration, prompt bank and model-facing prompt text are unchanged, so the evaluated protocol is the same. All 202 tests pass.

## Version 4.6: error handling

`spa/errors.py` holds one catalogue of error codes, each with a title, message, advice and automatic-handling rule; `docs/ERRORS.md` is generated from it and a test checks that they match. `tests/test_error_scenarios.py` (44 tests) covers every upload error (wrong file type, separators, ragged rows, duplicate or missing columns, identifying columns and values, text or out-of-range values, decimal commas, non-whole codes, blanks, wrong row counts, one participant repeated), quality warnings, the sensitive-topic confirmation and prohibited-content block, every provider outcome (budget exhausted, rate limit with retry, invalid key, access denied, context too long, rejected request, outage, uncertain submission), expired, failed, refused, empty, malformed, repetitive and copied batches, tampered handles, oversized requests and unusable comparison references. A fuzz script sent 42 malformed inputs to the API; each returned a specific code rather than a generic error. Browser QA with scripted fake providers confirmed: budget exhaustion stops all batches with the contact advice; rate limits are retried and complete; repetitive, empty and expired batches are resubmitted once and complete; a refusal is explained; wrong file types, bad cells and sensitive material show specific cards. The main template flow and the scan for source codes and M-style labels still pass. No paid provider call was made.

## Version 4.3: readable names, parallel batches, AI-only generation

Tests confirm that no MIDUS source code appears in any page, script, API response or download (templates, examples, variable guide, prompt preview, input check, prepared contexts, datasets, codebooks, comparisons and study findings), that prepared contexts translate back exactly so their signatures still verify, and that uploads using the readable names are accepted. Parallel-batch tests confirm four 25-person requests per dataset, correct participant ranges, preserved fixed values, rejection of off-boundary batch positions and assembly into one 100-person dataset. The free numerical demonstration endpoint is removed. Legacy tests run with `SPA_BATCH_SIZE=100` so they continue to check the original single-request protocol. Browser QA with a simulated provider covered a failed batch, retry, partial download and a scan of all visible text and downloaded files for source codes. The scientific core files are unchanged (hashes in `verification/build_checks.json`). Only an owner-configured public email is displayed; no contact address is fabricated.

## Version 4.2 additions

The original method prompt bank and MIDUS scientific engines are byte-identical to the prior release. New checks cover all eight original prompt renderings, all eight custom evidence renderings, read-only previews and rejected prompt fields, review requirements, signed evidence integrity, blank templates, zero-provider input checks, PDF extraction, encrypted/scanned/malformed input handling, and PDF size/page/text bounds. Browser QA uses private fictional API fixtures; paid provider execution and live Vercel deployment were not tested. The extraction endpoint and generation requests are tested with the real FastAPI application and mocked provider calls. Supporting papers have not been tested for empirical simulation fidelity.
