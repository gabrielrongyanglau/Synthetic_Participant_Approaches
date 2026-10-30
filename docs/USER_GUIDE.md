# Using the prototype

A synthetic participant approach (SPA) asks an AI to produce hypothetical participant records from specified information. This tool helps researchers choose and try eight approaches. The generated data require validation before supporting substantive research claims.

## First visit

1. Keep **MIDUS demonstration (recommended)** selected under *Which study?*. MIDUS is the Midlife in the United States study used in the original evaluation.
2. Choose what you want to explore and tick the information you have. The suggested approach is pre-selected; click any other card to choose it instead. One approach is used per simulation. The left-hand panel shows your choice and progress through the four steps.
3. Choose **Continue to inputs**. Keep **Free demonstration** selected; it uses invented records, makes no AI call and shows how the workflow and downloads work.
4. Choose **Check inputs**, review the summary that appears and tick its confirmation.
5. Choose **Generate demonstration dataset**, then **Download dataset and codebook (ZIP)** on *Your datasets*. It contains the CSV, variable codebook, metadata and supporting-information record. A numerical demonstration is not an AI performance result.

## Your own study

Select **Use your own study, questionnaire and participant data**. Enter the target population, construct definitions, verified citations, all exact questionnaire items, response scales, scoring and demographic categories. Each item needs a valid response range. Choose predictor/outcome roles. Mean and sum scores require every item. Define at least one demographic. The example study is fictional and is not a validated questionnaire.

Optional context and papers guide a custom adaptation. Add a research question, paste relevant empirical findings, or upload a PDF. Review all extracted text, including table order and symbols, remove unwanted sources and confirm the evidence checkbox. A DOI alone is not a paper upload. Free numerical demonstrations do not use literature evidence to generate values.

Choose AI generation to use your own participant inputs and reviewed evidence. There is no prompt editor. Our fixed method templates and server-controlled mapping/evidence instructions produce the request. Custom measures and literature-informed simulations have not been validated by the original MIDUS comparison.

## Upload the right information

Download the blank template ZIP and filled fictional example after finishing your measures. Read READ_ME.txt and input_variable_guide.csv. Keep CSV headers; enter one participant per row; remove direct identifiers. Use UTF-8 comma-separated CSV, numeric codes and allowed ranges.

| Public approach | Participant input |
| --- | --- |
| SPA1–SPA3 | No participant CSV. SPA3 uses a population description. |
| SPA4 | Demographic proportions. Fill each category; proportions sum to 1 within a demographic. |
| SPA5–SPA6 | At least 50 pilot records with demographics, psychological measures and outcomes. Exactly 50 are drawn without replacement. |
| SPA7 | At least 100 demographic profiles. |
| SPA8 | At least 100 demographic and observed psychological predictor profiles. Outcomes are generated. |

MIDUS pilots contain the listed score columns and both life-satisfaction outcomes. Blank predictors are permitted; outcomes must be observed. Custom pilots contain every defined raw item and demographic, all complete; composite scores are recalculated. Custom SPA8 uses observed predictor score columns or item-only predictor columns. Fixed missing predictors remain missing. Names, emails and source person IDs are unnecessary.

SPA5 receives pilot records and precomputed summaries. SPA6 receives pilot records and analyzes them within the model. SPA7 generates psychology and outcomes with fixed demographics. SPA8 generates outcomes with fixed demographics and predictors. Profile pools larger than 100 are sampled without replacement; exact-size pools keep their order.

## Start and wait

Review the time/funding notice, authorize sharing with OpenAI for AI runs, then check inputs. Fix any reported issues before continuing. Review the summary and confirm it. Any subsequent settings/input changes require another check. One simulation creates one dataset of 100 people.

AI generation may take up to one hour depending on variables, complexity and service availability. The interface shows elapsed minutes, latest status and check time. It polls an existing background request through short server calls, avoiding an hour-long Vercel function. No percentage is invented while the provider is generating.

Keep the tab open and your device awake. If a progress check fails, choose **Check progress again**. This reads the existing response, not a new paid simulation. If submission is uncertain, contact the team before trying another run. Budget exhaustion, provider outages and invalid model output remain possible; zero failures cannot be guaranteed. Repeated profiles and pilot matches are retained and flagged.

## Download and optional comparison

Download before refreshing or leaving. The prototype has no saved history. The codebook explains every exported column. Metadata records settings, provenance, quality flags and whether evidence was used. The supporting-information JSON records the reviewed text, not the original PDFs.

Optional human comparison uses observed records with the same measures. It is separate from generation and is not sent to OpenAI. Original MIDUS findings under *Study findings* are separate from visitor simulations. One visitor run cannot estimate a Monte Carlo confidence interval.
