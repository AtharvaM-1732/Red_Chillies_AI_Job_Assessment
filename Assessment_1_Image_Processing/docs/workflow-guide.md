# ComfyUI Workflow Guide — Assessment 1

This guide describes the two branches in `workflows/assessment1_workflow.json`.

## Overview

The workflow contains two independent pipelines:

- **Branch A:** Extend the missing background, then pass the result through an image-upscaling node.
- **Branch B:** Use a two-stage inpainting pipeline to reconstruct a masked area and then attempt to add a bicycle.

The branches are independent. They do not feed into one another.

## Prerequisites

1. Install and launch [ComfyUI](https://github.com/comfyanonymous/ComfyUI).
2. Put the checkpoint `Raymnants.3.0-sdxl.safetensors` in `ComfyUI/models/checkpoints/`.
3. Put the upscaling model referenced by Branch A in `ComfyUI/models/upscale_models/`.
4. Load the workflow JSON and confirm the model names resolve.
5. Upload the source images used by the workflow. If moving the workflow to another machine, reselect the images in the Load Image nodes.

## Branch A — Background extension

### Node path

`Node 1 (Load Image) → Node 2 (ImagePadForOutpaint) → Node 12 (VAE Encode for Inpainting) → Node 8 (KSampler) → Node 9 (VAE Decode) → Node 11 (ImageUpscaleWithModel) → Node 10 (Save Image)`

### Key settings

- Padding: 160 px left, 160 px right, 0 px top, 0 px bottom
- Feathering: 32
- KSampler steps: 25
- CFG: 5.5
- Sampler: `dpmpp_2m`
- Scheduler: `karras`
- Denoise: 1.0
- Save prefix: `assessment1_output1_outpainted`

The positive prompt asks for a photorealistic landscape and a seamless continuation of the existing scenery. The negative prompt discourages blur, distortion, artifacts, unnatural edges, text, watermarks, and oversaturation.

**Resolution note:** the workflow currently references `1x-ITF-SkinDiffDetail-Lite-v1.pth`. A 1× model does not increase image dimensions. Replace it with an appropriate scale-up model if the output must be larger than the input.

## Branch B — Object removal and addition

Branch B uses two inpainting stages. Its input is loaded by Node 6, and the checkpoint is loaded by Node 15.

### Stage 1 — Reconstruct a masked region

`Node 6 (Load Image) → Node 18 (VAE Encode for Inpainting) → Node 20 (KSampler) → Node 23 (VAE Decode)`

- Positive prompt: reconstruct the background naturally with consistent lighting, shadows, textures, and realistic details.
- Negative prompt: avoid people, duplicate objects, blur, artifacts, distorted textures, unnatural patterns, text, and watermarks.
- KSampler: 25 steps, CFG 5.5, `dpmpp_2m`, `karras`, denoise 1.0.

The decoded image from Node 23 is passed to Node 19 for Stage 2.

### Stage 2 — Attempt to add a bicycle

`Node 23 (VAE Decode) → Node 19 (VAE Encode for Inpainting) → Node 21 (KSampler) → Node 22 (VAE Decode) → Node 24 (Save Image)`

- Positive prompt: generate a realistic, correctly proportioned bicycle placed naturally on the ground with matching perspective, lighting, and shadows.
- Negative prompt: avoid floating bicycles, distorted wheels, duplicate bicycles, unrealistic proportions, blur, artifacts, text, and watermarks.
- KSampler: 25 steps, CFG 8, `dpmpp_2m`, `karras`, denoise 1.0.
- Save prefix: `assessment1_branchB_final`

### Mask requirement

Node 6's `MASK` output is connected to both Node 18 and Node 19. Confirm that the loaded image actually provides the intended mask. If it does not, create or edit the mask in ComfyUI before running the workflow.

The masked area controls where inpainting can change the image. For object removal, mask the object to remove. For object addition, mask the intended placement area. If the two stages need different mask regions, use separate masks for the stages rather than reusing one mask blindly.

## Run and verify

1. Load the JSON in ComfyUI.
2. Check that all checkpoint and upscaler files are available.
3. Select the correct source image(s).
4. Inspect the Branch B mask before execution.
5. Queue Branch A and Branch B independently.
6. Save the actual output images in the repository's `outputs/` directory.
7. Verify that each final image is landscape-oriented and at least 720 pixels in the required dimension(s), according to the assessment's interpretation of the minimum-resolution requirement.
8. Record the actual output dimensions and file formats in the README. Do not report results until the saved images have been checked.

## Troubleshooting

- **Missing model error:** confirm the checkpoint/upscaler filename and folder.
- **Missing input image:** reselect the image in the Load Image node.
- **No expected object change:** inspect the mask and confirm it covers the intended region.
- **Bicycle appears in the wrong area:** adjust the Stage 2 mask and prompt.
- **Output is not larger:** use a genuine upscaling model; the current 1× model will not enlarge the image.
- **Validation error:** check every required input socket before using a limited run.

## Workflow reproducibility

ComfyUI workflows store node configuration and connections, but they may reference local model files and input images that are not included in the JSON. To reproduce the result, provide the workflow JSON and make sure the recipient obtains the required model files and source images in accordance with their licenses.
