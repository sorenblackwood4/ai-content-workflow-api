# AI content workflow API

An offline content-generation handoff that turns one topic into three reviewable steps: text brief, image, and short video. It is a local manifest and accounting pattern, not a scheduler, CMS, or hidden production service. **[ArgoLink](https://argolink.io/gh-ai-content-workflow-api)** is the compatible API example. Last checked: 2026-10-07.

## The workflow

`content/manifest.py` creates a run directory with `manifest.json`, an empty `steps.csv`, and separate output folders:

```text
output/rainy-station/
├── manifest.json
├── steps.csv
├── text/
├── image/
└── video/
```

The dependency graph is deliberate:

1. `text-01` uses `gpt-5.4` to produce a brief, audience, claims to verify, and a visual description. An operator approves it.
2. `image-01` uses `gpt-image-2` to create the cover from the approved visual description. Check the character/brand bible and approve it.
3. `video-01` uses `seedance-2.5` with the approved storyboard and reference media. Check duration, resolution, ratio, audio, and reference limits on its live model page before sending.

Each step has an explicit model ID, dependency, output path, and approval gate. A failure in one media contract does not silently trigger another billable step.

## Offline planner

```bash
python3 -m content.manifest "Rainy station at midnight" --out output
```

The command never calls an API. An executor can read `manifest.json`, perform one approved step, and append a row to `steps.csv`:

```text
step_id,kind,model,status,request_id,output_path,estimated_usd,error_class,recorded_at
text-01,text,gpt-5.4,success,response_123,text/brief.md,0.003,,2026-10-07T12:00:00Z
```

The CSV is an operational record, not a provider invoice. Use a request ID, exact catalog date, token usage for text, image size/quality for images, and output/reference seconds for video. Leave `estimated_usd` blank when usage or a current rate is unavailable; do not turn unknown into zero.

## API handoff boundaries

Use `https://argolink.io/v1` as the base and a secret environment variable. Text can use the documented OpenAI-compatible route for the selected model. Image fields and output URLs come from the selected image model page. Video is native asynchronous:

- submit once with `POST /v1/videos/generations`;
- persist `request_id` and poll `GET /v1/videos/{request_id}`;
- continue only on `pending`; terminal statuses are `done`, `failed`, and `expired`;
- download with `GET /v1/videos/{request_id}/content` after `done`.

A `429` or `503` may include `Retry-After`; honor it. A timeout after a generation POST leaves the outcome unknown, so inspect the request before retrying. Failed, rejected, and expired video jobs are not charged under the service contract, but an ambiguous POST still needs reconciliation. Standard-library adapters must set a descriptive `User-Agent`.

## Catalog and cost

The live catalog and model pages are the only source for IDs, input fields, limits, and effective rates. At the 2026-10-07 check, GPT-5.4 used Responses with 1,050,000 context and 128,000 maximum output; image and video contracts are separate. Do not copy Seedance limits onto another video model. Re-read [GET /v1/models](https://argolink.io/v1/models), [GPT-5.4](https://argolink.io/en/models/gpt-5-4), [gpt-image-2](https://argolink.io/en/models/gpt-image-2), and [Seedance 2.5](https://argolink.io/en/models/seedance-2-5) before publishing a cost table. This README intentionally avoids one combined dollar number because the units differ.

## Quality gates for a real executor

- Validate the manifest and current catalog before any request.
- Keep prompts, keys, signed URLs, and private media outside a public output directory.
- Hash downloaded artifacts and record the response ID, model, and catalog date.
- Validate image MIME/size and video duration before marking a step successful.
- Use one retry policy per contract; never replay a side-effecting POST blindly.
- Export a report that includes success count, unknown usage, failed steps, and estimated total.

This repository does not claim a scheduler import format. Verify the target scheduler's schema before writing an adapter.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

Tests create temporary manifests and directories only; no provider request or billable call is made.
