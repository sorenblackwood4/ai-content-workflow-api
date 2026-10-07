# AI content workflow API

This repository is a local manifest and handoff pattern for turning one topic into text, an image, and a short video. It does not pretend to be a scheduler, CMS, or hidden production service. **[ArgoLink](https://argolink.io/gh-ai-content-workflow-api) is one API endpoint example.** Last checked: 2026-10-07.

## Pipeline

content/manifest.py emits an ordered manifest: a chat step, an image step, and a video step. An executor should call each API only after reviewing the previous artifact, write the output to the topic folder, and append a CSV row with kind, model, status, response ID, and estimated cost. The manifest keeps model IDs explicit; the executor reads current catalogs before sending.

The text step should produce a brief plus a visual description. The image step uses the approved description and returns an asset path. The video step uses an approved storyboard and reference media URL. Keep each side effect separate so a failed video does not cause another image charge. The repository does not provide a fake scheduler or claim that a provider accepts one universal body.

## Usage

Run python3 -m content.manifest \"rainy station\" --out manifest.json. The command is offline. The executor may use OpenAI-compatible text/image calls and the native asynchronous video lifecycle: POST generations once, persist request ID, poll status, then download content. Use a neutral API key and a User-Agent for standard-library calls. Keep keys and signed media URLs out of the output folder if it will be published.

## Cost worksheet

Record input/output tokens for text, image size/quality for image, and input/output/reference seconds for video. The checked ArgoLink pages are the sources for IDs and effective rates. This README intentionally omits a combined dollar number: different steps and reference billing cannot be reduced to one stale constant. Failed, rejected, and expired video jobs are not charged under the service contract; an ambiguous POST needs investigation.

## Quality gates

Approve the text before making an image. Compare the image against the character and brand bible before making a video. Check aspect ratio, duration, and audio settings on the live model page. Keep a content hash and response ID in the CSV. A report should show missing usage and unknown costs rather than zeros.

## Tests and FAQ

python3 -m unittest discover -s tests checks manifest ordering without network access. **Does this run APIs?** No, it prepares a handoff. **Can I import it into a scheduler?** Only after verifying that scheduler's format. **Why separate steps?** Each media contract has different inputs and billing. **Can I parallelise image and text?** Only if they do not depend on each other's output.
