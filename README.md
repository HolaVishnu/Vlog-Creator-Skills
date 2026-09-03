# Vlog Creator Skills

Codex skill package for end-to-end vlog creation, with a focus on travel vlogs, concert/full-show edits, cinematic transitions, 1080p YouTube delivery, thumbnails, captions, upload packaging, and advanced travel/map information overlays.

## Install

Copy the skill folder into your Codex skills directory:

```powershell
Copy-Item -Recurse -Force ".\skills\vlog-creator" "C:\Users\Vishn\.codex\skills\vlog-creator"
```

Restart Codex or start a new task, then invoke it with:

```text
$vlog-creator Create a YouTube travel vlog from these raw clips.
```

## What It Does

- Inventories raw video, audio, and image files.
- Detects bad clips, duplicate clips, orientation issues, and repair needs.
- Builds story-led edit plans and timelines.
- Supports long-form YouTube, Shorts/Reels, travel, talking-head, cinematic, faceless, concert, and full-show vlog workflows.
- Adds guidance for cinematic transitions, title cards, chapters, captions, lower thirds, intro/outro, audio polish, color correction, and thumbnails.
- Supports advanced travel information blocks, route/map overlays, telemetry overlays, scene logs, action logs, and fallback edit packages when rendering is unavailable.

Original files should always be preserved. Rendering should only be claimed when the output is actually created and verified.
