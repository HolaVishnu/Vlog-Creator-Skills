# Advanced Polish And Travel Overlays

Read this when the user asks for a world-class, cinematic, futuristic, highly informative, travel-focused, or data-rich vlog experience.

Use advanced polish to improve the viewer's understanding and feeling, not to cover weak story choices. Keep every overlay, transition, and animation tied to a real moment: location change, time jump, route progress, important performance beat, cost/tip, emotional turn, or visual reveal.

## Agent Edit Memory

Create durable project artifacts when the edit is more than a tiny rough cut:

- `project.json` or `timeline.json`: the current edit decision list, overlays, captions, music, export settings, and look choices.
- `scene-log.md` or `scene-log.json`: scene-by-scene observations, usable moments, bad/duplicate ranges, orientation issues, camera movement, audio quality, and travel/location clues.
- `actions.jsonl`: append-only edit actions with timestamp, source clip ID, timeline range, operation, and short reason.
- `review-notes.md`: human-readable QC notes for beginning, middle, end, and any user-reported problem ranges.

Use rationale notes for meaningful cuts and overlays, especially after user feedback. The log should explain why an edit was made without appearing in the rendered video.

## Transcript, Waveform, And Visual Review

When speech, singing, narration, or crowd response matters, prefer transcript-aware editing when tools are available. Use word/phrase timestamps to find hooks, repeated lines, dead air, crowd peaks, and chapter boundaries. If transcripts are unavailable, use audio waveform, loudness peaks, scene changes, and filmstrip contact sheets.

For important cut points, generate or request review aids when supported: short diagnostic clips, timeline filmstrips, waveform images, or start/middle/end stills. Use them to check pacing, sync, black frames, duplicate shots, bad focus, and bad transitions before exporting the full video.

## Cinematic Transition Palette

Choose transitions from the footage and music:

| Transition | Best use | Avoid when |
| --- | --- | --- |
| Hard cut | Live music, strong action, direct continuity | It creates audio clicks or visual confusion |
| Equal-power audio crossfade | Joins between takes or removed silence | It blurs an intentional beat or lyric |
| Cross dissolve | Gentle time/location shift, emotional breath | Inside a song without a camera stop |
| Dip to black | Major chapter, show start/end, dramatic pause | Overused between every clip |
| Sound bridge | Carrying applause, ambience, or narration over a visual change | The audio source is confusing or poor quality |
| Match cut | Similar framing/action across two clips | The match is weak or calls attention to itself |
| Motion cut / whip bridge | Fast travel, crowd movement, energetic scene change | Source footage lacks motion direction |
| Speed ramp | Arrival, movement, reveal, performance energy | It distorts singing, speech, or handheld shake |
| Ken Burns still | Photos, posters, tickets, maps, still frames | Faces/text crop badly or motion feels random |
| Subtle push-in | Emphasize a stage moment, reaction, or title | Constant motion makes the edit restless |

If the renderer cannot produce a chosen transition, put the exact transition in the edit package and use the closest verified render-safe fallback.

## Travel Information Blocks

For travel vlogs, add small informative blocks when they help the viewer follow the journey. Use only information from media metadata, supplied notes, transcripts, GPS files, or user-confirmed facts. Do not invent locations, dates, prices, distances, weather, song names, or venue names.

Useful block types:

- Location card: place name, date/time, short context, one visual cue.
- Route card: start, destination, distance, transport mode, estimated or actual travel time.
- Moment card: what is happening now, why it matters, quick tip, cost, or lesson.
- Performance card: artist/event name, section title, crowd or atmosphere note, chapter label.
- Practical card: ticket/entry note, food/place tip, safety note, camera/logistics note.
- Timeline card: day number, stop number, chapter, or progress through the route.

Place blocks in safe zones, keep them readable on mobile, and fade them in/out gently. Prefer 2-4 seconds for simple cards and 5-7 seconds for maps or dense travel context. Never cover faces, performers, signs the viewer needs to read, or subtitles.

## Telemetry, Map, And Camera Data Overlays

If the user supplies GPX, FIT, SRT telemetry, GoPro GPS metadata, DJI SRT files, or reliable phone metadata, consider an overlay pass:

- Map route with current position, trail, compass/heading, distance, altitude, and speed when relevant.
- Camera/log details such as timestamp, focal length, ISO, shutter, aperture, exposure compensation, or color temperature only when embedded or supplied.
- Generate transparent overlay videos when the overlay tool supports alpha, so the base edit remains non-destructive.
- Align telemetry to video using creation time or an explicit offset; document the offset and confidence.
- Include map/data attribution requirements in the edit package when using map tiles or external datasets.

For ordinary phone travel footage without telemetry, use tasteful location/title cards instead of pretending route data exists.

## Overlay Styling

Build a consistent overlay system before rendering:

- Define title, chapter, lower-third, caption, map, and data-card styles once per project.
- Use restrained animation: opacity, scale, position, and blur/fade are usually enough.
- Keep preview and export styling aligned when possible; if they differ, say so.
- Burn captions after overlays only when that prevents captions from being hidden.
- Use high contrast, clean typography, and short phrases; dense facts belong in the description or chapters.

## Adaptive Picture And Audio Polish

When supported, analyze the actual footage before grading: brightness, contrast, saturation, white balance, flicker, shake, loudness, noise, and clipped peaks. Record computed values in the edit log or EDL so the edit is repeatable.

Apply corrections gently:

- Fix exposure and white balance before adding a look.
- Match adjacent clips before applying a creative grade.
- Use loudness normalization, de-clicking, de-noise, high-pass, de-essing, and music ducking when available.
- Use short audio fades at clip joins to avoid clicks.

## Validation Gates

For advanced edits, verify these before calling the export final:

- The edit log and scene log exist for complex projects.
- User-requested problem ranges were specifically checked.
- Titles, captions, and data blocks are readable at 1080p and do not hide important action.
- Travel/location data is supported by metadata, files, or user confirmation.
- Preview/export differences are documented.
- The rendered file passes stream, duration, resolution, audio, orientation, and spot-check playback checks.
