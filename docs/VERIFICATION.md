# Verification

The scientific engine was previously independently run against all 8,000 original datasets and the full 2,709-person eligible human reference. All 6,374 mapped workbook cells passed, including 5,935 numerical results and 439 p-value display strings/significance decisions. The maximum absolute numerical difference was approximately 3.35 × 10⁻¹³. The original per-tab checks are in `verification/validation_summary.csv`.

This public, no-storage revision preserves the statistical calculations, study definitions, input-draw helpers and original representative prompt bank byte-for-byte. The pure output-schema and record-parsing functions are retained from the earlier generation module. Database, invitation and disk-checkpoint collection code has been removed. Original aggregate study statistics are unchanged.

Automated checks cover all eight input methods, every supported sample size from 100 to 1,000, pilot independence, the M5 summaries/M6 analysis distinction, exact fixed-input preservation, nulls, four-decimal generated values, duplicate flags, statistical formulas, intervals, pairwise comparisons and exports.

Public API tests use mocked OpenAI Responses and no database. They exercise all eight approaches across multiple 100-person batches, verify the fixed GPT-5.6 Luna/medium settings, check `store=false`, test temporary response signatures and expiry, reject unrelated/tampered response handles, verify post-receipt deletion requests, and check that a retrieval retry does not submit another generation. They also exercise public access without accounts, the absence of database requirements, origin/size checks, optional comparisons and request processing while filesystem writes are blocked.

The browser ZIP writer was checked independently using Python's ZIP reader for CRC integrity, UTF-8 content and larger file entries. JavaScript syntax and Python compilation checks passed. Browser checks used fictional API fixtures and exercised the no-sign-in demonstration, mocked AI generation, sequential method completion, result previews, duplicate flags and CSV/ZIP controls. These browser fixtures are not part of the distributed application.

All **83 tests passed** in 95.24 seconds. The environment and check details are recorded in `verification/`. Tests make no paid API calls. One non-failing test-client warning concerns the test HTTP library's future migration.

**A live Vercel deployment, paid OpenAI request and independent security audit were not performed.** The owner must validate a small fictional run after setting the actual production key. OpenAI temporarily retains background responses and applies its own data controls even though the application saves no datasets. Cleanup is best effort. No durable recovery, exactly-once submission or cross-tab session history is claimed.

Computational agreement reproduces the specified analysis and does not establish validity of individual prediction, intervention effects or every scientific interpretation.

## Study Findings charts

The chart payload copies the original `summary.csv`, `variables.csv` and `human.csv` values at full floating-point precision. Tests compare every supplied aggregate row with its source and check chart selection/scaling across all displayed distribution metrics and both relationship assessments. All 16 method/assessment scatterplot combinations are checked against the variable-level and human sources. Anxiety is excluded from these scatterplots exactly as in the primary 37-predictor comparison.

Browser checks covered chart rendering, confidence-limit labels, MIDUS 2/MIDUS 3 switching and the method selector. The chart explanations distinguish M7's actual predictor inputs from generated scores, and variable-specific available-run counts from method-level complete-statistic counts. Viewing the charts runs no model generation and stores no user datasets. Original statistical calculations and prompt templates are unchanged.
