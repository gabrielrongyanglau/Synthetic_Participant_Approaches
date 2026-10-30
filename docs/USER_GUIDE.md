# Using the toolkit

Start on **Choose an approach**. A synthetic participant is a hypothetical record, not a newly recruited person. Select the feature you want to explore, then the study setup and the information you can supply. The suggestion is based on the MIDUS comparison and does not guarantee validity for your study. You may select alternatives.

| Public approach | Information supplied | Generated values |
| --- | --- | --- |
| SPA1 Persona prompted | Study definitions | All values, using imagined personas |
| SPA2 Direct generation | Study definitions | All values directly |
| SPA3 Population guided | Definitions and a population description | All values |
| SPA4 Quota matched | Demographic proportions | Psychological responses and outcomes; constructed demographics fixed |
| SPA5 Pilot calibrated | 50 pilot records and toolkit-computed summaries | New complete records |
| SPA6 Pilot analysis guided | 50 pilot records; model instructed to analyze them | New complete records |
| SPA7 Demographic-only profiles | Observed demographics | Psychological responses and outcomes |
| SPA8 Demographic and psychological profiles | Observed demographics and predictors | Outcomes only |

SPA7 is original analysis M8 and SPA8 is original M7. Historical source files keep their original IDs; public downloads use SPA labels.

## Research purpose

For score distributions with pilot data, SPA5 is the suggested starting point and SPA6 is an alternative. For relationships with pilot data, SPA6 had smaller errors than SPA5, but both substantially overstated strengths. With observed psychological profiles, SPA8 simulates hypothetical outcomes. Without participant information, SPA2 is the simplest starting point. Demographic profiles can be preserved without establishing accurate psychological responses.

These uses inform preliminary exploration and human study planning. Synthetic results cannot establish a human hypothesis, a causal mechanism, measurement validity, individual prediction or a valid missing-value imputation. Do not use their correlations as empirical inputs to power calculations.

## Prepare and generate

Choose the MIDUS demonstration or define a custom study. Filled fictional examples illustrate the exact CSV structure. Custom inputs must match your declared codes; arbitrary uploaded column names are not automatically inferred or mapped. Rename your columns using the guide before upload.

Pilot approaches draw 50 separately for each method and repetition. Profile approaches require at least the requested number of people. Exact-size files retain their order; larger pools are sampled without replacement. Input pools can overlap, and exact-size pools recur. The seed controls input draws, not deterministic AI output.

The free demonstration uses fictional numerical rules and makes no AI requests. For a custom free demonstration, load the filled fictional study first. To use your own measures and participant inputs, select AI generation and supply the matching CSVs. Preview instructions and confirm permission to send the inputs to OpenAI. Each simulation is restricted to one approach and one dataset of 100 participants to conserve the research team’s API budget. Larger samples and repetitions are unavailable. Visitors using their own API keys is planned for a future update.

## Results and comparison

Allow approximately 5–20 minutes per AI simulation as a provisional planning estimate. Runtime varies with the questionnaire and provider demand. Budget or service limits can interrupt the simulation; contact the research team using the instructions displayed before generation. Keep the tab open, inspect quality flags and download results. Duplicates are retained. Fixed supplied values retain their precision and missingness; generated values have at most four decimals. The recommended ZIP download includes the dataset, `codebook.csv` and metadata. The codebook has one row per exported column, including demographic category labels, psychological definitions, scoring and whether values were generated or retained. Metadata contains the study setup, input provenance and method mapping, without API credentials or temporary access handles.

Optional comparison uses all supplied human records; demographic columns are unnecessary. It does not match generated people to real people. Custom references can supply computed construct scores or the raw items needed to derive them. MIDUS references use its predefined scores. Missing and constant values can leave statistics undefined; they are not replaced by zero.

The current single-run trial cannot estimate a confidence interval across user runs. The original study charts retain their 1,000-repetition intervals. Intervals describe the precision of mean performance against the fixed supplied reference. Custom pattern r is suppressed when fewer than three predictor coefficients are available, because two coefficients give a mechanically perfect positive or negative pattern correlation.

An independent human reference provides a stronger assessment of generalization than reusing generation inputs. The original reported MIDUS analyses used the full eligible reference, including participants who could supply generation inputs.

The **Study findings** page reports the original study, not your generated datasets. Its recommendations for other research settings are potential applications requiring separate validation.
