---
name: Diagram Artifacts and Review
description: Package editable diagrams, relocate generators safely, and verify source, PNG and native hierarchy before delivery.
---

# Reproducible artifacts

Keep each topic's source, editable PNG, preview when used, and explanation together. Preserve requested filenames. Group a large collection into presentation/reference/domain folders only when it helps navigation and stays within the assignment. Store outputs in `diagram/`, project-specific renderers/content in the project's `scripts/diagrams/`, and reusable helpers in this skill's `scripts/`. Do not move project business content into a global skill.

Resolve paths from script locations or explicit arguments, independent of the shell's working directory. When moving code, update imports, all generator consumers, output routing, README trees, companion source links and reproduction commands. Regenerate affected text and compare artifact hashes to prove a path-only refactor preserved models and rendered pixels.

The e-commerce package is a worked example: [project generators](../../../../e-commerce/scripts/diagrams/diagram_paths.py), [artifact index](../../../../e-commerce/diagram/README.md). Read these only when working in that project; do not copy its palette, canvas size, counts or storage decisions into unrelated projects.

## Native draw.io pipeline

1. Build native editable shapes/connectors in `.drawio`. Store nested child coordinates relative to their actual parent. Use source/target references or deliberate editable point routing; a screenshot embedded as one image is not an editable diagram.
2. Export an editable PNG using the available draw.io renderer. Discover its actual CLI/options rather than assuming an installed binary or installing tools silently. Retain the native model in the PNG. HTML/SVG previews can use a different rendering engine; visually compare the delivered artifact itself.
3. If the native renderer emits `mxGraphModel` metadata and compatibility requires an additional `mxfile` entry, call `drawio_core.finalize_png(source_path, png_path)`. It validates the existing payload against the source before adding compatibility metadata and retains IDAT pixel bytes. This is a metadata operation, not an image export.
4. Run the verifier with explicit paths, then inspect the image and native editor behavior. Keep actual renderer/version/fonts/export settings with verification evidence. Missing fonts can change layout; use fallbacks deliberately and report any unverified rendering difference.

## Shared scripts

`drawio_core.py` provides native cell construction, geometry helpers, PNG chunk/CRC parsing, compressed/uncompressed draw.io model reading, cell-reference validation, metadata parity and PNG finalization. It uses the Python standard library. The geometry helpers operate on orthogonal routes/rectangles; their use does not replace project-specific layout checks.

```bash
python3 -B .agents/skills/diagram-creator/scripts/verify_diagram.py path/to/view.drawio path/to/view.drawio.png --require-nested
python3 -B -m unittest discover -s .agents/skills/diagram-creator/tests -v
```

`--require-nested` checks for a real vertex inside a vertex on every page. It does not prove all intended ownership or geometric containment; reconcile that against the drawing contract and renderer. Omit it for views without structural containment requirements.

`--roundtrip path/to/reexport.png` compares PNG header/IDAT bytes. Use the same renderer version, fonts, scale and export settings; different encoders can produce different bytes for visually identical pixels. `--max-bytes N` applies an explicit delivery constraint, not a universal image-size rule.

The checker validates all embedded `mxfile`/`mxGraphModel` entries against source graph models, cell IDs, parents, cycles and referenced endpoints. It reads raw XML and compressed draw.io pages and PNG text metadata. It checks PNG structure/CRCs and pixel-stream preservation; open the image in a renderer to establish that pixels decode and look correct. It does not prove business semantics, route readability or editable interaction.

## Record observed review

Record source reconciliation, generator/checker results, visual inspection and native edit/re-export separately. State what was actually performed, including unavailable tools. For a pure script relocation with byte-identical final models/PNGs, hash parity can preserve previously recorded visual evidence; do not claim a new visual/editor session occurred.

A useful handoff includes paths, exact commands/results, evidence baseline, cuts, remaining design decisions and unavailable checks. PR publication follows the applicable delivery skill only when authorized.
