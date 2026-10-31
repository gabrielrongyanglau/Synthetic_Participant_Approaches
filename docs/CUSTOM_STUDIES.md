# Custom questionnaires

Custom-study generation extends the original score-level MIDUS prototype. It supports numeric item responses, user-defined psychological predictors/outcomes and one to eight categorical demographics. It does not validate citations, obtain questionnaire items automatically or establish psychometric validity. Optional reviewed PDF text or pasted findings can guide AI generation through a fixed server-controlled evidence layer. See [Prompt policy](PROMPT_POLICY.md).

## Definition

Enter a unique lowercase CSV code for each construct. Double underscores are reserved for generated item column codes, such as `support__i1`. Enter the construct definition, source, every item, numeric endpoints, scale anchors, integer/decimal response type, reverse-coded item positions and mean, sum or item-only scoring. Sources and exact item wording must be verified by the user.

A mean/sum score is calculated only when every item is observed. Reverse coding is `minimum + maximum - raw response`. Scores are rounded to four decimal places after aggregation. Item-only measures stay as separate items and are never combined into composites.

Demographic categories are optional and needed only for SPA4, SPA7 and SPA8. Define up to eight, with numeric codes. Continuous demographic fields are not supported in this extension. Define meaningful categories, such as age bands, where suitable.

## Inputs

Use **Check definition** or **Check and continue** on the Questionnaire step to validate the structure and create examples matching the declared columns. Download examples on the Inputs step. These records are invented numerical examples, not human observations.

- **Pilot input:** exactly 50 participants, one row each, with every demographic and, for each construct, either all of its item columns or one construct-score column. Scores are computed from items when items are supplied. SPA5 receives the records plus descriptive statistics, correlations and covariances calculated by the toolkit. SPA6 receives only records and is instructed to analyze them itself.
- **SPA7 profiles:** at least n demographic rows. Items and scores are generated.
- **SPA8 profiles:** at least n rows with demographics and observed predictor scores. Predictor scores may be supplied directly or as their item columns (scored by the toolkit). For item-only predictors, supply their item columns. Outcomes are withheld. No predictor items are invented when only a composite was supplied.
- **SPA4 target proportions:** one row per declared demographic category, with `variable`, `category`, `category_label` and `proportion`. Proportions add up to 1 within each demographic. The toolkit matches each demographic's proportions separately, so combinations across demographics are random.

CSV headers must match the guide. Missing fixed predictor values remain missing; nulls are not imputed. Generated items are required to be observed. Repeated generated profiles and pilot matches are flagged and retained.

## Evaluation

The toolkit generates and documents custom datasets. It does not compare them with human data. The original MIDUS findings do not show how closely a custom questionnaire, item-level generation, a different outcome or a different population is reproduced, so each needs its own check against human data.
