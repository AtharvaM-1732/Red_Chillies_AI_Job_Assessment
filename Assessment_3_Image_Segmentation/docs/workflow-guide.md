# Workflow Guide — Assessment 3

## Goal

Segment a requested object from an image and save both a mask and a cutout. The current target phrase is `Water Bottle`.

## Node-by-node flow

1. **Node 1 — Load Image:** supplies the source image.
2. **Node 4 — DownloadAndLoadFlorence2Model:** loads `microsoft/Florence-2-base` with FP16 precision and SDPA attention.
3. **Node 5 — Florence2Run:** runs `caption_to_phrase_grounding` using the phrase `Water Bottle`.
4. **Node 10 — Florence2toCoordinates:** converts Florence-2 output to coordinates.
5. **Node 6 — DownloadAndLoadSAM2Model:** loads `sam2.1_hiera_large.safetensors`, configured for CUDA and FP16.
6. **Node 7 — Sam2Segmentation:** uses the source image, SAM 2, and coordinates to produce a mask.
7. **Node 11 — MaskToImage:** converts the mask into an image.
8. **Node 13 — Save Image:** saves the mask using prefix `sam2_mask`.
9. **Node 14 — Join Image with Alpha:** uses the original image and mask as alpha to create a cutout.
10. **Node 15 — Save Image:** saves the cutout using prefix `sam2_cutout`.

## Using a different target object

Change Node 5's `text_input` from `Water Bottle` to a clear phrase for the object in the image, for example `red apple` or `dog`. Results depend on the model's grounding and the content of the image.

## Before running

- Verify the source image is selected in Node 1.
- Ensure all seven required custom node types are installed.
- Ensure Florence-2 and SAM 2 models load correctly.
- Check that the runtime supports the configured CUDA/FP16 settings.
- Queue the workflow only after validation succeeds.

## Output review

Inspect both outputs:
- The mask should identify the intended object without substantial background leakage.
- The cutout should preserve the object and have a transparent background where the mask excludes pixels.

If the wrong object is selected, try a more specific target phrase and inspect the coordinates/mask. Save actual outputs under the repository's `outputs/` folder. Record the actual dimensions and do not claim a metric until it has been measured.
