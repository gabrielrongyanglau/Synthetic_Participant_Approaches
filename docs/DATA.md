# Data and files

`data/examples/reference.csv` is an invented 2,709-row reference generated deterministically from measurement ranges and latent normal variables. It contains no actual MIDUS participants or empirical MIDUS coefficients. Its size illustrates the original workflow.

`data/examples/M1_R0001.csv` through `M8_R0001.csv` contain 100 illustrative records each. `M*_inputs.json` records the supporting invented pilots, summaries and fixed profiles. `make_examples.py` regenerates them. M5 has all 780 pairwise relationships among 38 predictors and two outcomes; M6 receives only pilot records. These files illustrate information flow, not the empirical performance of those prompts.

`data/original_study/` contains aggregate statistics recalculated from the original study and verified against the supplied workbook. It contains no participant records, original pilot records, private prompt audits or API credentials. The human reference statistics describe the full 2,709-person cohort. The old 542/2,167 split is used only in the legacy benchmark-reproduction/input helpers; it never restricts a comparison reference. The guided generation workflow uses supplied method-specific pools directly and needs no benchmark split.

Canonical participant columns are `participant_id`, the 38 psychological fields, six demographic fields, `life_satisfaction_MIDUS2` and `life_satisfaction_MIDUS3`. Variable definitions and declared missing codes are in `config/study.yaml`. The outcomes map to B1SSATIS and C1SSATIS. Generic uploads can use these output names or their source outcome names. Keep missing values blank or null. For original human input, cohort and identifier checks also apply.

An analysis bundle contains:

- `summary.csv`: metric/outcome/method, scorable-run count, mean and Monte Carlo CI.
- `comparisons.csv`: first-minus-second mean difference, adjusted CI and p-value, Welch df and significance.
- `variables.csv`: variable-specific distribution and relationship statistics and run counts.
- `human.csv`: reference sample sizes, means, SDs and outcome correlations for each variable.
- `metadata.json`: source label, reference size, dataset count, settings and provenance.
- `runs.csv` when available: repetition-level method metrics.

The original R export converter maps its documented column names to this schema. Raw CSV archive analysis is available through `analyse.py`; use it for recalculation or individual-run data. Aggregated uploads cannot reconstruct individual score distributions.

Synthetic output exports for M4, M7 and M8 include the fixed input values. Treat such files according to the permissions covering those inputs. Private reference and pilot datasets are omitted from download bundles.

## Guided inputs

`data/templates/demographic_proportions.csv` is a filled, invented example of marginal proportions for M4. Its columns are `field`, `category`, `lower`, `upper` and `proportion`. Use all six demographic fields, with proportions summing to 1 separately for each. Age rows give non-overlapping inclusive integer intervals; other rows give valid category codes. A `missing` category represents missing demographic values. Profiles preserve apportioned marginal counts, with independent permutations across variables.

`pilot.csv`, `M7_profiles.csv` and `M8_profiles.csv` contain column headers for uploads. Pilot data include all preset demographics, psychological variables and both outcomes. M7 profiles require only demographics and psychological variables; M8 requires only demographics. No outcome column or human benchmark is required for either profile method.

The new generation-only export has `M*_R*.csv` datasets and `metadata.json`. Its record identifies the information source, method, settings, quality flags and validation status. Optional comparison tables can be downloaded as CSVs. The original study results and user-generated runs are kept separate in the interface.

Fixed-profile run records include `input_rows_in_output_order`, a 1-based mapping from generated participant IDs to rows in the uploaded input file. Pilot draws record `pilot_input_rows`. Original source identifiers are not sent to the model. The mapping allows researchers to join their own identifiers back locally.
