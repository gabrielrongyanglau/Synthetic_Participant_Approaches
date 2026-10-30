# First-time user guide

A **synthetic participant** is a partly or wholly computer-generated participant record. A **synthetic participant approach (SPA)** is the combination of instructions and information used to create such records. These approaches do not recruit new human respondents. An AI model, or large language model (LLM), reads a prompt and produces values.

## Choose an approach

| Approach | Information used | Generated values |
| --- | --- | --- |
| M1 Persona prompted | Variable definitions; imagine a different person per row | All demographics, psychological scores and both life-satisfaction outcomes |
| M2 Ungrounded random | Variable definitions; generate records directly | All values; the “random” instruction is not probability sampling |
| M3 Population guided | Definitions plus a written description of the eligible population | All values |
| M4 Quota matched | Demographic proportions | Psychology and outcomes; constructed demographics are fixed |
| M5 Pilot calibrated | 50 actual pilot records plus tool-computed summaries | New complete records |
| M6 Pilot analysis guided | 50 actual pilot records; the AI analyses them itself | New complete records |
| M7 Demographic and psychological profiles | Actual demographics and psychological scores | Life satisfaction at both assessments only |
| M8 Demographic only profiles | Actual demographics | Psychological scores and both outcomes |

Choose according to your available information and intended purpose. Results from the original study guide interpretation; they do not guarantee accuracy for your own runs. M5 may suit illustrative score distributions, M6 exploratory pilot-informed simulations, and M7 hypothetical follow-up outcomes for existing profiles. All require validation before substantive inference or individual prediction.

## Prepare inputs

The study variables are already defined: 38 psychological predictors, age, sex, education, marital status, racial origin, religious preference, and life satisfaction at MIDUS 2 and MIDUS 3. The AI prompts refer to these assessments as Wave 1 and Wave 2. Use the variable guide for exact CSV names, ranges and category codes. Blank predictors mean missing values.

M1–M3 require no participant CSV. M3 needs a population description consistent with the study population. M4 needs a proportion table for all six demographics, each summing to 1. The tool matches these separate proportions; it does not reconstruct an observed joint demographic distribution.

M5/M6 need at least 50 pilot records, including both outcomes. Each method and repetition draws 50 separately, without replacement within a draw. M5 also receives precomputed statistics; M6 receives no such statistics. M7/M8 need at least as many profiles as requested output participants. An exact-size profile file is kept in order; larger pools are sampled. Draws across methods or repetitions can overlap, and exact-size pools recur. An input sampling seed controls these draws, not the AI's randomness.

Filled fictional examples are available for every upload type. They demonstrate the format, not actual human distributions. Use the free demonstration to practise without charges. It uses one repetition and invented numerical rules. Use AI generation to simulate using actual instructions and your selected inputs.

## Generate and download

No account or sign-in is needed. Select 100–1,000 participants and, if needed, up to five repetitions per approach. Check the total record count, preview the first batch's prompt and consent to sending inputs to OpenAI. All AI calls use the owner's key, GPT-5.6 Luna and medium reasoning.

Keep the progress page open. Each request generates 100 participants and saves a validated batch. If a progress check fails, keep this tab open and choose Check progress again. It retrieves the same temporary provider response. The application does not save the results. Refreshing or closing this tab loses them. Download all wanted datasets before leaving. All batches in a dataset use the same pilot/profile draw. Later batches do not receive generated records from earlier batches.

Download one CSV per complete dataset or the ZIP. `participant_id` links each generated outcome to its fixed inputs within that dataset. Original input row numbers are in the metadata, so you can join your source IDs privately. The download contains no API key. CSVs retain original variable codes and numeric category codes.

Duplicates and pilot matches are preserved and flagged in the metadata. Fixed input values stay exact, including nulls and their original precision. New values have at most four decimal places. Incorrect record counts, IDs, structure or ranges require review. Provider errors do not trigger automatic paid retries. If a large dataset is interrupted, received valid batches can be downloaded as a clearly marked partial CSV. OpenAI temporarily retains background responses and its separate retention policies still apply.

## Optional comparison

Supply a human reference CSV using the same psychological variables and outcomes. All eligible supplied records are used, with available observations for each correlation. No one-to-one pairing is assumed. The file is not sent to OpenAI or saved by the application. The original study findings are a separate screen and do not change with your inputs.

Distribution metrics assess mean differences, variability and full score distributions across 38 predictors. Relationship metrics compare 37 psychological–life-satisfaction correlations at each assessment, excluding anxiety. Lower errors and higher agreement indicate closer reproduction. High Pearson pattern correlation can coexist with large errors in relationship strengths. The screen explains each measure and its calculation.

Each dataset is scored separately. Confidence intervals describe the precision of average performance across scorable repetitions and are conditional on the fixed human reference. One repetition cannot produce a confidence interval. Welch comparisons use Bonferroni adjustment for the number of selected method pairs within each statistic/outcome. This is 28 pairs when all eight approaches are compared. Small numbers of repetitions provide limited precision. Missing or undefined statistics remain blank.

## Visual study findings

The Study findings page uses the original verified aggregates, not the datasets in your browser session. Summary cards identify M5’s closest generated psychological-score distributions, M6’s closest relationships among approaches generating psychological scores, and M7’s closest relationships overall. M7 retains actual psychological predictors, so its low distribution error is explicitly separated from generated-score fidelity.

Use the assessment selector to switch relationship results between MIDUS 2 and MIDUS 3. The distribution selector changes between full score distributions (Wasserstein distance), standardized mean error and variability error. Dot-and-interval charts display means with 95% confidence intervals and numerical bounds. Hover or focus points for full method labels and scored-run counts. A common-scale chart contrasts Pearson pattern correlation with ICC(A,1) and Lin’s CCC.

The final scatterplot lets you inspect all 37 primary psychological correlations for one method and assessment. Points near the diagonal have closer human and average simulated correlations. Each variable uses its own available runs; counts need not match the complete-statistic counts in the method-level charts. Original detailed tables and adjusted pairwise comparisons remain below the charts. On narrow screens, charts can be scrolled horizontally. No new simulations or API charges are involved in viewing this page.
