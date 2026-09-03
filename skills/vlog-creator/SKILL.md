---
name: vlog-creator
description: Create vlogs from raw video, audio, and image media, including footage analysis, edit plans, rough-cut rendering, polish guidance, and export QC.
metadata:
  short-description: End-to-end vlog creation
---

# Vlog Creator

Turn raw media into a story-led vlog. Prefer automation when the environment supports it, but be exact about limits: render only when the necessary media, codecs, storage, and tools are actually available; otherwise produce an executable edit package that another editor or human can complete without guesswork.

Use this priority hierarchy for every decision:

**Story -> emotion -> pacing -> audio -> visuals -> graphics -> transitions -> packaging**

## Operating Modes

- **Automatic production:** inventory supplied media, choose highlights, build an edit decision list, render a verified rough cut when FFmpeg-compatible rendering is available, and continue polish/QC as far as supported.
- **Edit package:** when rendering, transcription, stabilization, reframing, music, captions, or editor automation is unavailable, create a complete handoff with exact clip decisions, timeline, effects, captions, color recipe, export settings, and next editor actions.
- **Review or repurpose:** inspect an existing cut, project, transcript, or plan and recommend the smallest changes that improve story, pacing, audio, visual continuity, platform fit, and delivery quality.
- **Consultation:** help a beginner choose a workflow, preset, structure, or editor without implying that media was edited.

When the user provides or mentions uploaded media, inspect attachments and reachable workspace paths before asking for a path. Treat the absence of a typed path as unknown, not unavailable.

## Production Gate

Before claiming production is possible, identify:

- Source media found: videos, standalone audio, still images, transcripts, music/SFX, logos, fonts, intro/outro assets, GPS/telemetry files, map data, and creator notes.
- Available tools: FFprobe/FFmpeg, video editor/project APIs, speech-to-text/caption tools, image tools, stabilization/reframe tools, map/telemetry overlay tools, motion-graphics tools, and enough disk space.
- Constraints: missing codecs, corrupt files, variable frame rates, mixed orientation, clipped audio, wind/noise, duplicates, missing coverage, unknown music rights, or unsupported effects.
- Target preset: platform, aspect ratio, resolution, frame rate, duration range, tone, captions, and output format.

Preserve originals. Write inventories, proxies, manifests, project files, exports, and fallback packages to new locations. Do not overwrite source files or previously rendered outputs.

Use `scripts/check_video_tools.py` when tool availability is unclear. It reports whether FFprobe-based inventory and FFmpeg rough-cut rendering are available.

## Automated Workflow

1. **Inventory:** run `scripts/inspect_media.py INPUT [INPUT ...] --output inventory.json` for folders or individual media files. It records duration, video/audio fields, still-image metadata when FFprobe can read it, orientation, and probe errors without modifying originals.
2. **Analyze:** assign stable IDs, detect duplicates or near-duplicates where feasible, flag bad clips, identify highlights, note story beats, mark clip categories, and record technical repair needs.
3. **Build story:** choose a hook, setup, turning points, payoff, and closing beat. If the footage cannot support the intended story, name the gap and use the closest honest workaround. For complex travel or event edits, create a scene log and keep an action log so decisions, fixes, user-requested changes, and QC checks remain traceable.
4. **Select clips:** create a clip-decision table with one row per source: stable ID, exact in/out, KEEP/CUT/B-ROLL/AUDIO/STILL decision, timeline use, issue/repair note, and beginner-friendly reason. For concert, performance, ceremony, or event footage where the user's goal is to enjoy full songs or complete moments, preserve the meaningful duration instead of collapsing everything into a short highlight unless they explicitly ask for a short cut.
5. **Create timeline:** use `assets/rough-cut-manifest.example.json` as the manifest schema when rendering a rough assembly. Include only supported video clips with exact `in` and `out` times.
6. **Render when supported:** run `scripts/render_rough_cut.py manifest.json output.mp4`. It refuses to overwrite existing output or sources and verifies readable H.264/AAC MP4 output.
7. **Polish:** apply or specify audio cleanup, music/SFX, stabilization, cropping/reframing, orientation fixes, color correction/grade, captions, titles, lower thirds, intro/outro, transitions, travel information blocks, route/map overlays, and subtle motion graphics only when they serve the story.
8. **Quality control:** verify any rendered file exists and has readable streams, duration, resolution, frame rate, and audio. Review beginning, middle, and end; for final delivery, review full playback where feasible.
9. **Package for upload:** when the user is preparing YouTube or social publishing, provide title options, description, chapters when possible, tags, hashtags, and thumbnail concepts or generated thumbnails when supported.

The bundled renderer creates a verified rough assembly, not automatically a fully polished vlog. Call the export "finished" only after the story, sound, picture/color, captions/graphics, and delivery QC passes are actually completed or accurately represented in a project/export workflow.

## Presets

Use [platform and style presets](references/presets.md) when the user names a platform/style or leaves the target open. Defaults:

- **YouTube long-form:** 16:9, 1920x1080 or source-native 4K, 24/25/30 fps matching source, story-led chapters, accurate captions, title/description/tags/thumbnail prep. For full-show, concert, or performance edits, favor watchable continuity and complete performances over aggressive short-form trimming.
- **Shorts/Reels/TikTok:** 9:16, 1080x1920, 30 or 60 fps matching source, immediate hook, safe-zone captions, tighter pacing.
- **Travel vlog:** place-first hook, route/context graphics, ambience, cinematic B-roll, restrained transitions, title cards for major locations or scenes, and optional map/telemetry/data overlays when supported by real metadata or user-provided notes.
- **Talking-head vlog:** clean dialogue, jump-cut rhythm with B-roll covers, subtle reframes, lower thirds where useful.
- **Cinematic vlog:** measured pace, intentional silence, motivated music, stabilization where helpful, natural correction before grade.
- **Faceless vlog:** stronger narration/text structure, detail shots, screen capture or stock only when rights are clear, captions and labels carry more context.

## Reference Routing

Load only the files needed for the current request:

- Footage inventory, highlights, bad clips, duplicate handling, and EDL fields: [footage analysis](references/footage-analysis.md).
- Story structure, clip selection, pacing, transitions, and retention passes: [editorial workflow](references/editorial-workflow.md).
- Audio cleanup, music/SFX, captions, titles, lower thirds, intro/outro, color, stabilization, crop, and reframe: [post-production](references/post-production.md).
- Advanced cinematic transitions, travel information blocks, map/telemetry overlays, scene logs, action logs, waveform/filmstrip review, and futuristic on-screen information design: [advanced polish and travel overlays](references/advanced-polish-and-overlays.md).
- Platform/style presets and export targets: [presets](references/presets.md).
- Editor-specific handoff and automation boundaries: [software guidance](references/software-guidance.md).
- Render verification, fallback packages, and final delivery checks: [delivery and quality control](references/delivery-and-quality-control.md).

## Deliverables

Return the chosen mode, target preset, source inputs, original-preservation status, creative direction, clip decisions, timecoded timeline, automation performed, output paths, verification results, assumptions, and remaining user decisions.

When rendering is unavailable, fill `assets/fallback-edit-package.template.md`. Include the precise reason rendering is unavailable once under **Production status**, then provide exact executable instructions rather than vague advice.

For beginners, use plain language and short ordered steps. Define editing terms briefly when first used, but keep the skill proactive: do the inventory, analysis, manifest, render, captions, or handoff work when tools and media allow it.

## Guardrails

- Do not publish, upload, schedule, or use third-party music/SFX/assets unless the user explicitly authorizes it and rights are known.
- Do not invent footage, captions, source metadata, edits, renders, or software capabilities.
- Do not destroy or overwrite originals. Keep workflows non-destructive and reversible.
- If a tool, codec, media file, or permission is missing, continue with unaffected sources and produce a precise fallback package.













