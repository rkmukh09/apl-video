# apl-video

Explainer videos for American Padel Labs, made from resource-center articles on americanpadellabs.com.

## How a video gets made
1. **Storyboard.** Each video starts as a storyboard table in the SEO blog Google Doc (tab "6. LinkedIn, X, and video"): scene, length, frame, on screen, talk track, changes. A copy lives in `storyboards/<slug>.json`. Every fact comes from the live article.
2. **Review frames.** One still per scene is rendered and linked in the table before the full render.
3. **Render.** `render/` draws every frame in Python (Pillow + OpenCV) and encodes with FFmpeg: 1080 x 1920 vertical first, 16:9 on request.
4. **Voice and post.** Raj records the talk track (CapCut), or sends audio and the video is timed to it. Channel copy comes from the article-distribution skill.

## Layout
- `brand/` brand kit: `BRAND.md` (website and Instagram style, rules), fonts (Bebas Neue, Inter, Figtree), logo, photos.
- `storyboards/` one JSON table per video (rows match the Google Doc table).
- `render/apl.py` scene drawing and timeline for the dimensions video (v1). `render/render.py` renders it in parallel segments; `render/sound.py` makes the sound effects.
- `render/styles/` style tests for the Instagram looks (B with Inter, C with Figtree).

## Run
```
pip install numpy opencv-python-headless pillow
cd render && python3 render.py && python3 sound.py
ffmpeg -i video_noaudio.mp4 -i sfx.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest out.mp4
```

## Status (Nov 24, 2026)
- Padel court dimensions: v1 rendered (look A). Storyboard reordered: space, concrete slab, court.
- Padel court cost: storyboard only.
- How a padel court gets built: storyboard only.
- Padel court maintenance and the Wema PadelPro: storyboard only (needs Wema demo footage).
- Design is open: A (website), B (Instagram, Inter), C (Instagram, Figtree). Decide on the first finished video.
