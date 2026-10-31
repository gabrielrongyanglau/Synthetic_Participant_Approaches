# Fixed prompts

Visitors choose an approach and provide structured study information. There is no system-prompt or user-prompt editor. Arbitrary prompt/model fields are rejected by the run API. Prompt previews are read-only.

`prompts/methods.json` retains the eight original representative templates byte-for-byte, with the original study's numbering. `spa/prompts.py` selects the template for each SPA through `spa/numbering.py`, so SPA7 (demographic-only profiles) and SPA8 (demographic and psychological profiles) receive exactly the templates evaluated for those procedures.

For a custom study, `spa/custom.py` fills the same template placeholders with the declared measures, records and output schema. A fixed server-owned system layer explicitly maps original cohort/wave/life-satisfaction wording to the declared population and predictor/outcome fields. It specifies raw item generation and local scoring. This is an adaptation, not an identical reproduction of the original evaluation.

Research context, pasted findings and papers are not accepted. Version 6.5 removed them, so the AI receives only the fixed method template, the declared study and the inputs the chosen approach needs.

The full study context is included in the signed input digest. Changes after preparation invalidate the request. Downloads include metadata identifying the adaptation and the original method-bank checksum. The application does not independently validate measurement sources.
