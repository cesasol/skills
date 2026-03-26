---
name: comfyui
description: >
  Run image generation workflows on a local ComfyUI instance (localhost:8188).
  Use this skill when the user wants to generate images using ComfyUI — including
  FLUX.2 text-to-image generation or any workflow that requires queuing a prompt
  to the ComfyUI API. Trigger when users mention ComfyUI, "generate an image",
  or want to run a diffusion workflow locally.
---

# ComfyUI — Local Image Generation

Run FLUX.2 image-generation workflows on a local ComfyUI server via its REST API.

**Server:** `http://localhost:8188`

## Critical Rules for Agents

1. **Always verify the server is running** before queuing work: `curl -s http://localhost:8188/system_stats | head -c 200`.
2. **Randomize seeds** for each generation unless the user asks for reproducibility. Generate a random integer (up to 2^53 - 1).
3. **Poll for completion** — the `/prompt` endpoint returns immediately with a `prompt_id`; you must poll `/history/{prompt_id}` until outputs appear.
4. **Download results** to the current working directory so the user can see them.

---

## API Reference

### Check server status

```bash
curl -s http://localhost:8188/system_stats
```

### Queue a workflow

```bash
curl -s -X POST http://localhost:8188/prompt \
  -H 'Content-Type: application/json' \
  -d '{"prompt": <API_FORMAT_WORKFLOW>}'
```

Returns `{"prompt_id": "uuid"}`.

### Poll for completion

```bash
curl -s http://localhost:8188/history/<prompt_id>
```

Returns `{}` while running. When done, returns a map keyed by `prompt_id` containing `outputs` per node. Look for `SaveImage` nodes — their outputs have `images: [{filename, subfolder, type}]`.

### Download a generated image

```bash
curl -s -o output.png 'http://localhost:8188/view?filename=<filename>&subfolder=<subfolder>&type=output'
```

### Cancel current job / clear queue

```bash
# Cancel running job
curl -s -X POST http://localhost:8188/interrupt

# Clear pending queue
curl -s -X POST http://localhost:8188/queue \
  -H 'Content-Type: application/json' \
  -d '{"clear": true}'
```

---

## Available Workflows

### Text to Image — FLUX.2 Klein 4B (`flux2-klein-txt2img`)

**File:** [workflows/flux2-klein-txt2img.json](workflows/flux2-klein-txt2img.json)

Generates images from text using the lightweight FLUX.2 Klein 4B model with Qwen 3 4B as the text encoder. Uses CFG guidance (positive + negative prompts) and a configurable resolution calculator. No input image needed.

**Pipeline:** FluxResolutionNode → EmptyFlux2Latent → CLIPTextEncode (pos/neg) → CFGGuider → SamplerCustomAdvanced → VAEDecode → SaveImage

#### Configurable nodes

| Node ID | Class | Field | Default | Description |
|---------|-------|-------|---------|-------------|
| `97` | CLIPTextEncode | `text` | *(sample prompt)* | Positive prompt — describe what you want |
| `90` | CLIPTextEncode | `text` | `""` | Negative prompt — describe what to avoid |
| `93` | RandomNoise | `noise_seed` | `177265768842890` | Seed; randomize per run |
| `86` | CFGGuider | `cfg` | `5` | CFG scale (classifier-free guidance strength) |
| `85` | Flux2Scheduler | `steps` | `20` | Sampling steps |
| `85` | Flux2Scheduler | `width` / `height` | `1024` / `1024` | Output dimensions (overridden by resolution node) |
| `98` | FluxResolutionNode | `megapixel` | `"1.5"` | Target megapixels (`"0.5"`, `"1.0"`, `"1.5"`, `"2.0"`) |
| `98` | FluxResolutionNode | `aspect_ratio` | `"3:4 (Golden Ratio)"` | Aspect ratio preset |

#### Resolution presets (node `98`)

Common `aspect_ratio` values: `"1:1"`, `"4:3"`, `"3:4 (Golden Ratio)"`, `"16:9"`, `"9:16"`, `"3:2"`, `"2:3"`, `"21:9"`. Set `custom_ratio: true` and `custom_aspect_ratio: "W:H"` for non-standard ratios.

#### Models

| Component | File | Directory |
|-----------|------|-----------|
| Diffusion | `flux-2-klein-4b.safetensors` | `Flux2.Klein/` |
| Text Encoder | `qwen_3_4b.safetensors` | `text_encoders/` |
| VAE | `flux2-vae.safetensors` | `vae/` |
| LoRA | `lenovo_flux_klein9b.safetensors` | `Flux.2 Klein 9B-base/` |

#### Example: generate from text

```bash
# 1. Read the workflow template, patch it, and queue
WORKFLOW=$(cat workflow.json \
  | jq '.["97"].inputs.text = "A futuristic city at sunset, cyberpunk aesthetic, neon lights"' \
  | jq '.["90"].inputs.text = "blurry, low quality, text, watermark"' \
  | jq '.["93"].inputs.noise_seed = 98765' \
  | jq '.["86"].inputs.cfg = 5' \
  | jq '.["98"].inputs.megapixel = "1.5"' \
  | jq '.["98"].inputs.aspect_ratio = "16:9"')

PROMPT_ID=$(curl -s -X POST http://localhost:8188/prompt \
  -H 'Content-Type: application/json' \
  -d "{\"prompt\": $WORKFLOW}" | jq -r '.prompt_id')

# 2. Poll until done
while [ "$(curl -s http://localhost:8188/history/$PROMPT_ID | jq 'keys | length')" = "0" ]; do
  sleep 2
done

# 3. Download result
FILENAME=$(curl -s http://localhost:8188/history/$PROMPT_ID \
  | jq -r ".[\"$PROMPT_ID\"].outputs[\"9\"].images[0].filename")
curl -s -o result.png "http://localhost:8188/view?filename=$FILENAME&type=output"
```

---

## Standard Agent Procedure

When the user asks to generate an image with ComfyUI:

1. **Check server:** `curl -s http://localhost:8188/system_stats`
2. **Read the workflow JSON** from the `workflows/` directory (`flux2-klein-txt2img.json`)
3. **Patch the JSON** with user parameters (prompt, negative prompt, seed, cfg, resolution)
4. **Queue:** `POST /prompt` with the patched workflow
5. **Poll:** `GET /history/{prompt_id}` every 2-3 seconds until outputs appear
6. **Download:** `GET /view?filename=...&type=output` and save to cwd
7. **Show the user** the output path and, if supported, display the image

Always set a new random seed unless the user specifies one or asks to reproduce a previous result.
