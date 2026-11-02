> Approaches are numbered SPA1–SPA8 as in our proposal. Files in `data/original_study/` and the offline archive use the original study's numbering, in which 7 and 8 are swapped; `spa/numbering.py` relabels them when the toolkit loads them. Custom-study definitions and examples are described in CUSTOM_STUDIES.md.

# Data and files

`data/examples/` holds the MIDUS demonstration inputs, built by `tools/make_midus_examples.py` from the linked MIDUS 2 and 3 file (available to registered users through ICPSR, and never stored in this repository). `SPA4_proportions_example.csv` gives the actual demographic proportions of all 2,709 participants, one row per category (for example 43.63% male). `SPA5_pilot_example.csv` and `SPA6_pilot_example.csv` (50 rows each) are generated participants who reproduce the distributions and correlations of the calibration pool (542 people), the pool from which the original study drew its pilots. `SPA8_profiles_example.csv` (100 rows, demographics and psychological scores) and `SPA7_profiles_example.csv` (the same 100 people's demographics) reproduce the evaluation pool (2,167 people). Generated participants come from a Gaussian copula: every value is one observed in MIDUS, and the variables keep their observed rank correlations. Spouse or partner items are blank at the rate observed for each marital status. No generated record matches a real participant, and generated records are no closer to real participants than real participants are to each other. `MIDUS_examples_report.json` records how closely the files match their pools. No individual MIDUS records are distributed. The invented 2,709-row reference used by the tests is generated in memory by `spa.simulation.invent_reference`, so it is not stored.

`data/original_study/` contains aggregate statistics recalculated from the original study and verified against the supplied workbook. It contains no participant records, original pilot records, private prompt audits or API credentials. The human reference statistics describe the full 2,709-person cohort. The old 542/2,167 split is used only in the legacy benchmark-reproduction/input helpers; it never restricts a comparison reference. The guided generation workflow uses supplied method-specific pools directly and needs no benchmark split.

Canonical participant columns are `participant_id`, the 38 psychological fields, six demographic fields, `life_satisfaction_MIDUS2` and `life_satisfaction_MIDUS3`. Variable definitions and declared missing codes are in `config/study.yaml`, keyed by MIDUS source codes for reproducibility. The website and all downloads use the readable names in `spa/public.py` instead (for example `optimism_overall`, `age`); the server translates in both directions, so source codes never appear in the interface or in generated datasets. Generic uploads can use these output names or their source outcome names. Keep missing values blank or null. For original human input, cohort and identifier checks also apply.

An analysis bundle contains:

- `summary.csv`: metric/outcome/method, scorable-run count, mean and Monte Carlo CI.
- `comparisons.csv`: first-minus-second mean difference, adjusted CI and p-value, Welch df and significance.
- `variables.csv`: variable-specific distribution and relationship statistics and run counts.
- `human.csv`: reference sample sizes, means, SDs and outcome correlations for each variable.
- `metadata.json`: source label, reference size, dataset count, settings and provenance.
- `runs.csv` when available: repetition-level method metrics.

The original R export converter maps its documented column names to this schema. Raw CSV archive analysis is available through `analyse.py`; use it for recalculation or individual-run data. Aggregated uploads cannot reconstruct individual score distributions.

Synthetic output exports for SPA4, SPA7 and SPA8 include the fixed input values. Treat such files according to the permissions covering those inputs. Private reference and pilot datasets are omitted from download bundles.

## Guided inputs

SPA4 takes target proportions, one row per demographic category, with the columns `variable`, `category`, `category_label` (for reference only), `lower`, `upper` and `proportion`. Proportions add up to 1 within each demographic. Age bands use `lower` and `upper` (whole years within the eligible range, without overlaps), and the template starts from the bands in `config/study.yaml`. A row with category `missing` gives the share with no recorded value. Percentages that add up to 100 are converted, and rounding differences up to 0.02 are rescaled with a warning. The toolkit constructs 100 profiles that match each demographic's proportions separately, with independent permutations across variables. The other uploads use one row per participant and one column per variable. SPA5 and SPA6 take a pilot sample of exactly 50 people with all preset demographics, psychological variables and both outcomes; all 50 are used, in order. SPA7 takes exactly 100 demographic profiles and SPA8 exactly 100 demographic and psychological profiles, one row per synthetic participant, in order. Neither needs an outcome column.

The generation export has `SPA*_R*.csv` datasets and `metadata.json`. Its record identifies the information source, method, settings, quality flags and validation status. The original study results and user-generated runs are kept separate in the interface.

Fixed-profile run records include `input_rows_in_output_order`, a 1-based mapping from generated participant IDs to rows in the uploaded input file. Pilot records list `pilot_input_rows` (always rows 1–50). Original source identifiers are not sent to the model. The mapping allows researchers to join their own identifiers back locally.
