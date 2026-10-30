# Verification

The original scientific engine was independently compared with all 8,000 final datasets and the full eligible human reference of 2,709 participants. All 6,374 mapped workbook cells passed, including 5,935 numerical values and 439 p-value display strings or significance decisions. The maximum absolute numerical difference was approximately 3.35 × 10⁻¹³. The historical per-tab checks are retained in `verification/validation_summary.csv`.

The original MIDUS study definition, representative prompt bank, sampling helpers, statistical formulas and source aggregate files are unchanged. Public labels now follow the revised proposal: SPA7 is original M8 and SPA8 is original M7. Display mapping changes no source values or generation procedures.

## Current checks

The suite covers all original input methods, sample sizes, fixed-value preservation, missing values, numerical precision, duplication flags, statistical formulas, intervals, pairwise comparisons, exports and public background-response lifecycle. Provider requests are mocked; tests make no paid calls. The original-study chart payload is checked against the full-precision sources, including all 16 method/wave scatterplot combinations.

Additional tests cover custom questionnaire validation, reverse coding, complete-item mean/sum scoring, all eight custom generation procedures, matching templates, fixed predictor precision, pilot summary separation, server routes, score-only and mixed item/score human references, zero errors for identical references, suppression of uninformative two-coefficient pattern r, public method mapping and signed custom background responses. Altered context data are rejected before retrieval.

Python compilation and JavaScript syntax are checked. The browser ZIP writer is independently checked with Python's ZIP reader. Archive checks exclude credentials, caches, virtual environments and private participant data. The test log and environment details are recorded in `verification/`.

Browser QA uses private static fixtures produced by the real API test client. It checks custom study setup, complete pilot recommendations, progression to generation, a 100-person fictional dataset, updated study chart labels and the SPA8 relationship advantage. This is frontend QA, not a live provider or Vercel deployment test. Preview fixtures are not distributed.

## Limits

Custom item-level generation is a new functional extension. Computational tests establish implementation behavior, not empirical fidelity for new measures, populations or outcomes. Sources and questionnaire validity require human verification. Hypothesis testing, causal claims, individual prediction, imputations and effect-size assumptions for power calculations need separate evidence.

No paid OpenAI call, live Vercel deployment test or independent security audit was performed. The owner should check a small fictional production run using the configured key. Provider retention rules apply despite temporary application processing. Durable recovery and exactly-once submission are not claimed.

## Research-funded trial and codebooks

The public interface and request schema now limit simulations to one approach, one dataset and 100 participants. Tests reject larger or repeated runs before provider access, including submissions using an older larger signed plan. Historical offline engines and original study results are unchanged.

Dataset responses provide a column-matched codebook for MIDUS and custom studies. Checks cover all exported columns, the four example MIDUS codes raised during review, generated-versus-fixed provenance, custom items and composite scoring, demographic inclusion and UTF-8 codebook CSV parsing. New tests cover optional contact/estimate settings and sanitized budget-related provider errors without automatic retries. Browser QA checks the visible planning estimate, funding notice, disabled larger samples/repetitions, single approach selection, dataset/codebook download controls and demographic fields.

The interface states that generation may take up to one hour depending on variables, complexity and service availability. This is a planning estimate, not a measured performance result. Only an owner-configured public email is displayed; no contact address is fabricated.

## Version 4.2 additions

The original method prompt bank and MIDUS scientific engines are byte-identical to the prior release. New checks cover all eight original prompt renderings, all eight custom evidence renderings, read-only previews and rejected prompt fields, review requirements, signed evidence integrity, blank templates, zero-provider input checks, PDF extraction, encrypted/scanned/malformed input handling, and PDF size/page/text bounds. Browser QA uses private fictional API fixtures; paid provider execution and live Vercel deployment were not tested. The extraction endpoint and generation requests are tested with the real FastAPI application and mocked provider calls. Supporting papers have not been tested for empirical simulation fidelity.
