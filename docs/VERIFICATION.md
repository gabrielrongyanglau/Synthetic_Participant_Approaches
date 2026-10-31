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

## Version 6.4: layout and file encoding

The Overview no longer shows the four summary figures. On the Approach page, the Recommended tag sits under the approach name, so it no longer overlaps the Fits column. The PDF upload control is aligned with its label. Every CSV download, including those inside ZIP files, now starts with a UTF-8 byte order mark, so Excel shows characters such as the en dash in "18–34 years" correctly. A completed example downloaded with the mark was uploaded unchanged and passed Check inputs. All 212 tests pass.

## Version 6.3: clarity review

The Overview no longer has the two-ways panel or the goals note. It introduces MIDUS once and says the toolkit can be tried out with the MIDUS study or used with your own. Every page was read in workflow order for terms used before they are explained. The research goal and questionnaire pages no longer mention approach numbers, the decision path names each approach, the pilot question explains what a pilot sample is, and recommendation reasons refer to the proposal in place of Table 6. The SPA6 alternative is described as the AI analysing the pilot records itself, since the toolkit always calculates SPA5's summaries. For Goal 1 with measured psychological scores, the reason now states plainly that there is nothing to generate for Goal 1 and how to choose SPA5. Approach descriptions for your own study refer to your outcomes, where they previously named MIDUS life satisfaction. The Inputs step stops with a clear message when SPA4, SPA7 or SPA8 is chosen without demographic categories. Upload help, the variable guide and the results-table headings use plain wording, and the Glossary again explains the measures in the results table. All 211 tests pass.

## Version 6.2: statuses, completed examples and overview

Each workflow step in the side navigation now reads to do, locked or completed. Every upload on the Inputs step offers a blank template and a completed example with fictional values, and the completed example was uploaded unchanged and passed Check inputs. The Overview describes the two ways to use the toolkit: the MIDUS demonstration that repeats the proposal's setup, or your own study.

## Version 6.1: study-first flow

The steps follow the supplied revised design: choose your study, research goal, questionnaire (own study), your situation, approach, inputs (own study), check and generate, and datasets. The MIDUS demonstration skips the questionnaire and inputs steps and shows its example inputs on Check and generate. A step stays locked until the steps before it are complete. Compare with human data is removed from the interface, the API, the error catalogue, the tests and the guides. The overview content and the Errors and help page are kept, with the overview's step list updated to the new order. Recommendations, generation, batching, uploads and downloads are unchanged. Browser QA with a simulated provider at 1280 px and 390 px completed a MIDUS SPA5 run and a fictional custom SPA8 run through the new steps. All 211 tests pass.

## Version 6.0: research console

The interface follows design B: a top status bar, side navigation with step statuses, separate pages for the seven steps and the reference material, and an inspector with the current selections, the study evidence for the chosen approach and an activity log. The approach page adds a table of all eight approaches with their study results, read from the verified study data. Goal 2 is one option, worded after Prof Kim's draft, and both goals use the same Table 6 recommendations (SPA2 with no data, SPA4 with proportions, SPA5 with a pilot, SPA7 with demographic profiles, SPA8 with demographic and psychological scores). Earlier goal names are accepted and mapped onto the two goals. Generation, batching, error handling, uploads, downloads and comparison are unchanged and were exercised end to end in a browser with a simulated provider at desktop and phone widths: a MIDUS SPA5 run, choosing an approach from the table, comparison with the fictional reference, changing the goal after a run, clearing the session, a custom-study SPA8 run, the reference pages and Start over. Fonts are served from the app, so the content security policy still allows no third-party requests.

## Version 5.1: guided questions

Step 1 now asks two or three yes/no questions about what the researcher has (for example whether pilot data have been collected), which lead to one recommended approach from Table 6. Other approaches that fit are collapsed. The MIDUS demonstration always uses the supplied example inputs, so no upload appears after choosing it. Custom studies need only a title, and SPA3 asks who the participants are. A fictional MIDUS reference lets demonstration users practise the comparison step. Changing the study or editing a custom measure no longer resets the chosen approach. Browser QA covered every question path at 1280 px and 390 px. All 215 tests pass.

## Version 5.0: goal-first flow

The interface follows the proposal. Step 1 asks for the research goal (Goal 1: reproduce psychological scores; Goal 2: reproduce relationships among variables), then the information the researcher has now, and recommends an approach from Table 6 with the study result behind it. Step 2 asks once which study to use. The MIDUS demonstration uses the example inputs automatically, with an optional replacement file. Own studies upload only what the approach needs, and demographic categories are needed only for SPA4, SPA7 and SPA8. Tests cover the Table 6 mapping for every goal and stage (SPA2 with no data, SPA4 with proportions, SPA5 with a pilot and SPA6 for relationship strength, SPA7 with demographic profiles, SPA8 with demographic and psychological scores) and custom studies without demographics. Browser QA at 1280 px and 390 px completed MIDUS and custom runs through the new flow. The scientific core, prompts and statistics are unchanged. All 213 tests pass.

## Version 4.6.2: SPA4 target proportions

SPA4 again takes target proportions, one row per demographic category, as in version 4.2.0. No participant data are needed. The quota construction and the SPA4 prompt are unchanged. New tests cover each proportions error (missing demographic, unknown variable or category, repeated category, invalid proportion, totals other than 1, invalid or overlapping age bands, missing columns), automatic conversion of percentages and rescaling of rounding differences, custom-study templates built from declared categories, and plan signatures after browser number serialisation. Browser QA confirmed the SPA4 template download, a valid upload through to a completed dataset, the error card for proportions that add up to 0.798 and the note for percentages. The example proportions are fictional. SPA5 and SPA6 text now states exactly 50 pilot participants throughout. All 213 tests pass.

## Version 4.6.1: wording

Interface text, error messages, the variable guide and the codebook were reworded into plain statements without em dashes or semicolons. A browser scan of every visible page and a scan of the generated variable guide and codebooks found none of the listed patterns. Two preserved files, `spa/study.py` and `spa/workflow.py`, changed in message strings only, and their hashes are updated. The study configuration, prompt bank and model-facing prompt text are unchanged, so the evaluated protocol is the same. All 202 tests pass.

## Version 4.6: error handling

`spa/errors.py` holds one catalogue of error codes, each with a title, message, advice and automatic-handling rule; `docs/ERRORS.md` is generated from it and a test checks that they match. `tests/test_error_scenarios.py` (44 tests) covers every upload error (wrong file type, separators, ragged rows, duplicate or missing columns, identifying columns and values, text or out-of-range values, decimal commas, non-whole codes, blanks, wrong row counts, one participant repeated), quality warnings, the sensitive-topic confirmation and prohibited-content block, every provider outcome (budget exhausted, rate limit with retry, invalid key, access denied, context too long, rejected request, outage, uncertain submission), expired, failed, refused, empty, malformed, repetitive and copied batches, tampered handles, oversized requests and unusable comparison references. A fuzz script sent 42 malformed inputs to the API; each returned a specific code rather than a generic error. Browser QA with scripted fake providers confirmed: budget exhaustion stops all batches with the contact advice; rate limits are retried and complete; repetitive, empty and expired batches are resubmitted once and complete; a refusal is explained; wrong file types, bad cells and sensitive material show specific cards. The main template flow and the scan for source codes and M-style labels still pass. No paid provider call was made.

## Version 4.3: readable names, parallel batches, AI-only generation

Tests confirm that no MIDUS source code appears in any page, script, API response or download (templates, examples, variable guide, prompt preview, input check, prepared contexts, datasets, codebooks, comparisons and study findings), that prepared contexts translate back exactly so their signatures still verify, and that uploads using the readable names are accepted. Parallel-batch tests confirm four 25-person requests per dataset, correct participant ranges, preserved fixed values, rejection of off-boundary batch positions and assembly into one 100-person dataset. The free numerical demonstration endpoint is removed. Legacy tests run with `SPA_BATCH_SIZE=100` so they continue to check the original single-request protocol. Browser QA with a simulated provider covered a failed batch, retry, partial download and a scan of all visible text and downloaded files for source codes. The scientific core files are unchanged (hashes in `verification/build_checks.json`). Only an owner-configured public email is displayed; no contact address is fabricated.

## Version 4.2 additions

The original method prompt bank and MIDUS scientific engines are byte-identical to the prior release. New checks cover all eight original prompt renderings, all eight custom evidence renderings, read-only previews and rejected prompt fields, review requirements, signed evidence integrity, blank templates, zero-provider input checks, PDF extraction, encrypted/scanned/malformed input handling, and PDF size/page/text bounds. Browser QA uses private fictional API fixtures; paid provider execution and live Vercel deployment were not tested. The extraction endpoint and generation requests are tested with the real FastAPI application and mocked provider calls. Supporting papers have not been tested for empirical simulation fidelity.
