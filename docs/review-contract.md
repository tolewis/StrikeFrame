# Vision Review Contract

## Purpose
Structured output contract for multimodal creative review in StrikeFrame.

## Output file
- `<asset>.vision-review.json`

## Required top-level fields
- `version` — contract version string
- `model` — model id used for review
- `host` — review host base URL
- `channel` — target channel (`x`, `linkedin`, `generic`, etc.)
- `persona` — target persona/profile (`tim-operator`, etc.)
- `source_image` — reviewed image path
- `source_config` — optional config path if known
- `created_at` — ISO timestamp
- `overall_score` — float 0-10
- `channel_fit_score` — float 0-10
- `copy_visual_fit_score` — float 0-10
- `readability_score` — float 0-10
- `slop_risk` — `low|medium|high`
- `verdict` — `pass|warn|fail|reject`
- `should_reject` — boolean
- `confidence` — `low|medium|high`
- `summary` — one-line summary
- `reasons` — array of short rejection/concern bullets
- `fixes` — array of suggested fixes
- `raw_response` — original parsed model payload or text excerpt for debugging

## Verdict semantics
- `pass` — meets threshold for the selected channel/persona
- `warn` — usable only with revision
- `fail` — below target quality; should not ship
- `reject` — obviously bad / slop / off-brand / wrong-for-channel

## Threshold defaults
### Generic
- `>= 9.0` → `pass`
- `7.5 - 8.9` → `warn`
- `5.0 - 7.4` → `fail`
- `< 5.0` → `reject`

### Tim/X
- overall must be `>= 9.0`
- copy-to-visual alignment must be `>= 9.0`
- slop risk must be `low`
- otherwise downgrade to at least `warn`, often `fail`/`reject`

## Storage policy
- Contract docs live in repo under `docs/`
- Prompt files live in repo under `prompts/`
- Generated review JSON belongs next to the reviewed output asset
- Scratch/test renders for calibration belong in `/mnt/raid/Data/tmp/openclaw-builds/katya/...`
