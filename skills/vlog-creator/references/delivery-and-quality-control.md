# Delivery And Quality Control

Read this when preparing a render, final export, troubleshooting note, or fallback package.

## Render Verification

Do not claim an export exists until checking the actual file. Verify:

- File exists, is not empty, and opens.
- Readable video stream.
- Readable audio stream when audio is expected.
- Duration is plausible and matches the selected timeline.
- Resolution, aspect ratio, frame rate, codec/container, and audio settings match the target.
- Orientation and framing are visibly correct, especially for phone footage and any ranges previously reported as rotated.
- Beginning, middle, and end play correctly; final delivery should get full playback where feasible.

If the export fails, inspect the error and retry only with a targeted change such as relinking a source, freeing storage, changing a codec, or exporting a short diagnostic range. After repeated unchanged failures, stop and produce the fallback package with the error evidence.

## Final Passes

| Pass | Check |
| --- | --- |
| Story | Hook, clear middle, payoff, no confusing detours |
| Continuity | No accidental black frames, mismatched action, or bad sync |
| Audio | Dialogue intelligible, music/SFX not masking speech, no abrupt changes |
| Picture | Exposure, white balance, reframes, and stabilization hold up |
| Captions/graphics | Accurate, readable, well timed, clear of faces and controls |
| Export | Filename, folder, settings, streams, duration, and playback verified |
| Upload package | Title, description, chapters, tags, hashtags, and thumbnail are present when requested |

## YouTube Packaging

For YouTube deliverables, provide practical upload text after the edit is known:

- Title options that name the subject, event, or value without inventing venue, city, date, or song names.
- A description with a clear first paragraph, chapters when timeline timings are known, a short subscribe prompt if appropriate, rights/credit note when music or performances are involved, and relevant hashtags.
- Tags as a comma-separated list under YouTube's 500-character tag limit; favor artist, event type, genre, format, and audience intent over spammy or unsupported terms.
- Thumbnail concepts or generated thumbnails using strong frames from the actual footage when available. Verify generated thumbnail files exist, are 1280x720 for YouTube, readable, and have text that is large enough to scan on mobile.

## Fallback Package

When direct rendering or final polish is not supported, fill `assets/fallback-edit-package.template.md` with:

- Production status and exact limitation.
- Source inventory with stable IDs and probe results.
- Creative direction.
- Clip decisions, one row per supplied source.
- Complete timecoded timeline from `00:00.000` to the end.
- Audio/SFX map with licensing status.
- Captions, titles, lower thirds, intro/outro, and graphics instructions.
- Color and reframe recipe.
- Export settings.
- YouTube or platform packaging: title, description, chapters, tags, hashtags, thumbnail concept or file path when requested.
- One exact completion action in the user's selected editor.

Publishing, scheduling, or uploading requires explicit user authorization.



