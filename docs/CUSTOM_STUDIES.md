# Custom questionnaires

Custom-study generation extends the original score-level MIDUS prototype. It supports numeric item responses, user-defined psychological predictors/outcomes and one to eight categorical demographics. It does not validate citations, obtain questionnaire items automatically or establish psychometric validity. Optional reviewed PDF text or pasted findings can guide AI generation through a fixed server-controlled evidence layer. See [Prompt policy](PROMPT_POLICY.md).

## Definition

Enter a unique lowercase CSV code for each construct. Double underscores are reserved for generated item column codes, such as `support__i1`. Enter the construct definition, source, every item, numeric endpoints, scale anchors, integer/decimal response type, reverse-coded item positions and mean, sum or item-only scoring. Sources and exact item wording must be verified by the user.

A mean/sum score is calculated only when every item is observed. Reverse coding is `minimum + maximum - raw response`. Scores are rounded to four decimal places after aggregation. The same rules apply to human raw items used for comparisons. Item-only measures remain separate items in the comparison; they are not silently combined into composites.

Define demographic information for every custom study so the delivered dataset contains demographics as well as the requested psychological variables. Define categories with numeric codes. Continuous demographic fields are not supported in this extension; define meaningful categories, such as age bands, where suitable.

## Inputs

Use **Check definition and prepare templates** to validate the structure and create examples matching the declared columns. Download examples on Prepare and generate. These records are invented numerical examples, not human observations.

- **Pilot input:** at least 50 complete records containing all raw items and demographics. Scores are recomputed from items. SPA5 receives the records plus descriptive statistics, correlations and covariances calculated by the toolkit. SPA6 receives only records and is instructed to analyze them itself.
- **SPA7 profiles:** at least n demographic rows. Items and scores are generated.
- **SPA8 profiles:** at least n rows with demographics and observed predictor score columns. For item-only predictors, supply their item columns. Outcomes are withheld. No predictor items are invented when only a composite was supplied.
- **Quota input:** `field,category,proportion`, with proportions summing to one for every declared demographic. The toolkit matches marginal proportions separately; it does not reconstruct observed joint demographic combinations.
- **Human reference:** predictor/outcome scores or the raw items needed to calculate them. Demographics are not needed. Use all intended reference records and report whether this reference overlaps generation inputs.

CSV headers must match the guide. Missing fixed predictor values remain missing; nulls are not imputed. Generated items are required to be observed. Repeated generated profiles and pilot matches are flagged and retained.

## Analysis

Distribution errors use the declared predictor scores; if there are no predictors, they use the defined measure scores. Correlations compare each predictor with each outcome. Distribution statistics average required variable-level errors within each dataset. Relationship MAE and sign agreement require every declared predictor–outcome correlation for that outcome to be calculable. ICC(A,1) and CCC need at least two coefficients. Pattern r needs at least three coefficients with variation. Undefined results remain blank.

Means and approximate 95% intervals use the available dataset-level statistics and the original Monte Carlo mean-interval formula. Welch comparisons use Bonferroni correction for the selected method pairs within each metric/outcome. The current trial permits only one run, so user-run confidence intervals and method comparisons are unavailable. The reusable analysis engine retains these calculations for offline use. Results are conditional on the supplied reference and the generated runs.

A custom questionnaire's fidelity is not established by the original MIDUS findings. Item-level generation, different outcomes and populations require separate empirical evaluation.
