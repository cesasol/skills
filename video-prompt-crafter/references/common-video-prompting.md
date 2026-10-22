# Common Video Prompting

Shared rules for Wan 2.2, Wan 3.0, FLUX 3 Video, and Gemini Omni. Each model reference adds its own
syntax and limits on top of these.

## Direct a Shot, Not a Picture

An image prompt describes one frame. A video prompt describes **what changes**: the subject's
action as it unfolds, the camera's path, how light or weather shifts, and what is heard. A prompt
that only lists objects and adjectives produces a static camera in an undefined void.

A complete shot covers, roughly in this order (skip slots that do not apply):

1. **Medium or style**, when it must not read as live action ("1990s hand-drawn cel animation").
2. **Shot size, angle, and camera movement**: "Low tracking shot at ground level".
3. **Subject and appearance**: specific, visible traits ("a red fox with a frost-tipped tail").
4. **Action as it unfolds**, with speed and amplitude: "trots, slows, then stops and looks back".
5. **Setting and background motion**: "birch trunks, snow sifting from branches".
6. **Light**: source, direction, quality, time of day.
7. **Color and lens**: palette, focal length, depth of field.
8. **Sound** (models with audio): dialogue, ambience, effects, music.

## Beat Budget

A beat is one visible change: an action, a camera move, a reveal. Models compress, skip, or blur
beats they have no time for.

| Clip length | Beats that land |
| ----------- | --------------- |
| 5 s | 1-2 (one action plus one camera move) |
| 8-10 s | 2-3, or 2 shots |
| 12-20 s | 3-5, or 2-4 shots |
| 30 s | A beginning, a turn, and an end; 5-8 shots at most |

- Count the beats out loud in the prompt: "Three keys strike, one after another. A pause. Then the
  carriage returns with a sharp bell ding." Counting beats is more reliable than a summary verb.
- Join beats with sequence words: "then", "gradually", "finally", "as it lands".
- Avoid high-frequency motion the model cannot control ("shakes its head three times a second").
- Too little action for the length gives a slow, padded clip. Add background motion (drifting
  clouds, swaying grass) instead of more subjects.

## Camera

- One framing term, one movement term, one subject action per shot. "Low tracking shot" is clear;
  "low aerial handheld orbit push-in" is not.
- Write the camera as a sentence: "The camera slowly pushes in on her face." Pair a move with its
  pace or duration: "pushes in from wide to close over six seconds".
- For a still frame, say so: "locked-off camera", "fixed shot, camera static".
- Sequence compound moves instead of stacking them: "The camera rises above the trees, then tilts
  down toward the lake."
- Each move carries intent: push-in = intimacy or tension; pull-out = scale or isolation; tracking
  = travelling with the subject; orbit = importance; locked-off = stillness and focus.

Vocabulary that all four models respond to:

| Kind | Terms |
| ---- | ----- |
| Shot size | extreme close-up, close-up, medium close-up, medium shot, full shot, wide shot, extreme wide / establishing shot |
| Angle | eye level, low angle, high angle, overhead / top-down, aerial, Dutch angle, over-the-shoulder, POV |
| Movement | locked-off / static, pan left/right, tilt up/down, push in / dolly in, pull back / dolly out, tracking, truck left/right, orbit / arc, crane up/down, handheld, drone fly-through, crash zoom, whip pan |
| Lens and focus | 24mm wide-angle, 35mm, 50mm, 85mm telephoto, macro, fisheye, anamorphic, shallow depth of field, deep focus, rack focus |
| Time | slow motion, time-lapse, hyperlapse, real time |

## Light

Light has the greatest single effect on quality. Name the source, direction, and quality: "low
sunrise light from frame left, long blue shadows on the snow", not "moody lighting". Useful terms:
golden hour, overcast, moonlight, practical lights, neon, firelight, fluorescent, rim light,
backlight, side light, soft light, hard light, high contrast, low key, volumetric light shafts.

## Image-to-Video

- **Prompt the motion, not the scene.** The image already sets subject, setting, and style.
  Re-describing it invites the model to reimagine the frame instead of animating it.
- Refer to the subject generically ("the fisherman", "she") and say what moves, how, and where the
  camera goes. Name briefly anything that must stay fixed ("his face stays the same").
- First and last frames: describe the path between them, in order. Keep the camera simple, and keep
  both frames related (same subject, scene, and camera).
- Chain clips by using the last frame of one clip as the first frame of the next.

## Sound (Wan 3.0, FLUX 3 Video, Gemini Omni)

Four layers, each tied to something visible:

- **Dialogue**: speaker + verb + colon + quoted line: `The trucker in the faded cap says: "This
  coffee tastes like mud."` Give voice traits (age, accent, tone, pace). Keep lines short enough
  to speak in the time available (about 2.5 words per second).
- **Ambience**: name sources, not moods: "rain ticking on a metal awning, distant traffic".
- **Effects**: tie each to its cause: "as the cup hits the tile, one sharp ceramic snap".
- **Music**: style, instruments, and when it enters. Name a music bed once for the whole clip.

The models add dialogue, music, and captions unprompted. Close each prompt with the ones the user
does not want: "No dialogue. No music. No subtitles." A quoted line with no visible speaker can
render as on-screen text, so anchor it to a speaker or write "voiceover".

## On-Screen Text

Quote the exact words and say where and how they appear: `a chalk sign above the counter that
reads "OPEN LATE"`. Keep it short and physical (signs, title cards, lower thirds). Long copy, small
type, and logos are unreliable in video; say so in the description sentence when the user needs
them exact.

## Multi-Clip Continuity

- Write a fixed character and setting description once and paste it **word for word** into every
  clip's prompt.
- Keep one look across clips: the same light, palette, lens, and film format.
- Carry sound across the seam: "the rain continues", "the music builds into the chorus".

## Aspect Ratio by Use

Pick from the ratios the target model accepts (each reference lists them).

- `16:9` cinematic scenes, YouTube, landscapes, ads; `21:9` widescreen film looks
- `9:16` Shorts, Reels, TikTok, phone-first ads, standing portraits
- `1:1` social feed loops, product turntables
- `4:3` or `3:4` vintage TV, archival looks, portrait interviews

## Common Mistakes

| Mistake | Fix |
| ------- | --------------------------------------------------- |
| A still-image caption with no motion | Add the action as it unfolds and a camera move |
| Four actions in a 5-second clip | Cut to the strongest 1-2 beats or split into clips |
| Camera unstated, subject drifts | Name the camera, or write "locked-off camera" |
| Stacked camera moves | One move per shot; sequence the rest with "then" |
| "Cinematic, epic, stunning" | Name lens, light, and palette instead |
| Image-to-video re-describes the image | Describe only motion, camera, sound |
| Duration, fps, or ratio inside the prompt | Settings line (Gemini Omni length excepted) |
| Unwanted captions, music, or invented lines | End with "No subtitles. No music. No dialogue." |
