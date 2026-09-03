# Software Guidance

Read this when translating an edit plan into a tool, project file, or editor-specific handoff.

State the editor-neutral action first, then map it to the user's editor when known. Verify version-sensitive menu paths from the installed interface or current official docs before giving exact labels.

| Action | Premiere Pro | DaVinci Resolve | Final Cut Pro | CapCut |
| --- | --- | --- | --- | --- |
| Organize media | Project panel bins, labels, markers | Media Pool bins, markers, metadata | Events, Favorites, keywords | Albums, favorites, tags |
| Rough cut | Sequence matching target | Timeline on Edit page | Project in Event | Project timeline |
| Trim | Trim handles, Razor only for deliberate splits | Trim handles, Blade for deliberate splits | Clip edges, split at beat changes | Clip edges, split at beat changes |
| B-roll | V2 above dialogue | Higher video track | Connected clip | Overlay track |
| Audio | Essential Sound, light cleanup, keyframes | Fairlight cleanup and faders | Audio inspector and keyframes | Noise reduction/voice enhancement and volume |
| Captions | Caption/transcript workflow | Subtitle track | Captions | Auto captions corrected manually |
| Color | Lumetri correction and match | Color page correction and match | Color inspector | Adjust controls |
| Export | Target preset and in/out range | Deliver page | Share/export | Export panel |

Use `scripts/check_video_tools.py` before direct rendering when tool availability is unclear. Automation can create inventories, manifests, rough assemblies, caption drafts, project instructions, and repeatable file organization. It cannot replace judging story, rights, or final playback. If a requested editor API is unavailable, produce an editor-neutral EDL and a click-by-click handoff for the selected editor.

For beginners, split handoff instructions into **Required edit** and **Optional polish**. Required edit must complete the deliverable; optional polish should be skippable.
