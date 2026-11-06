# llm-brain intro films

Run from `tools/intro-video` using the committed lockfile:

```bash
npm ci
npx tsc --noEmit
npm run build:ontology
```

`LlmBrainOntology30` is a caption-led silent film: 1920×1080, 30 fps, exactly 900 frames / 30 seconds. The output is `out/ontology-30.mp4`. The build uses Remotion's supported `--muted` flag to omit the audio track entirely. For Remotion Studio use `npm run dev` and select `LlmBrainOntology30`.

The build requires these supplied 16:9 images; it stops with explicit missing paths if any are absent. No substitute artwork is generated:

- `public/ontology/information-field.webp`
- `public/ontology/reuse-field.webp`
- `public/ontology/ontology-atlas.webp`

Artwork uses `Img` / `staticFile` and frame-derived motion. Typography uses macOS system fonts: Helvetica Neue, Apple SD Gothic Neo, SF Mono / Menlo. No font files or external requests are added. Render on macOS for the intended Korean typography; a different OS can change font metrics and needs a fresh visual check. The ivory `#fbfaf7`, ink `#111111`, violet `#7c3aed`, blue `#2563eb`, thin rules, paper texture and editorial layout follow `assets/banner.svg`.

Timeline: fragmented information 0–5s; source → claim → knowledge 5–12s; evidence inspection 12–19s; artifact reuse 19–25s; closing title and URL 25–30s. Relationships follow `schema/ontology.yaml`: `source supports claim`, `claim compiled_into knowledge_page`, `artifact derived_from knowledge_page`, `artifact guided_by procedure`. The evidence display is a synthetic example. Stored status, trust and validity fields describe recorded metadata and do not guarantee factual truth. The film makes no model-version claims.

The original 60-second `LlmBrainIntro16x9` and `LlmBrainIntro9x16` compositions and their commands remain available. `build:all` continues to render those two original films only.

After supplying the images, render and inspect representative frames and the complete film for image crop, Korean text, relationship directions, readable timing and final URL. Typechecking alone does not establish visual acceptance.
