# APL video brand kit

Sources: americanpadellabs.com (Nov 2026) and instagram.com/americanpadellabs (viewed Nov 23, 2026).

## Website
- Navy: hsl(217 42% 31%) #2C4A72 (header/footer), deep navy hsl(220 100% 20%) #002266, white.
- Headlines: Bebas Neue (all caps). Body: system sans. Raj also uses Figtree.
- Logo: white court-icon mark with AMERICAN / PADEL LABS (brand/logo.png).

## Instagram
- Footage first: drone overheads of courts, glass close-ups, real play, the van; some film/polaroid frames.
- On-screen text: white, sentence case, clean sans (Figtree), centered; one short headline plus a smaller line under it.
  Examples: "AI can't build a court", "Go outside, touch glass", "Tired of booking courts? / Walk outside and play anytime."
- Logo as a small white watermark; profile mark is the logo on a black circle.
- Colors come from the footage: turf green, charcoal/black, white. Navy isn't used.
- Tone: short, dry, confident. Captions like "First come, first serve."

## Rules for every video
- Facts only from the live page the video is about.
- Feet first, meters in parentheses.
- Recommended footprint 36' x 69' (ring beam, access, machinery, gameplay).
- Never show the sand grade. Don't present partner (FSC, Padel Box) projects as APL builds.
- Vertical 1080 x 1920 first; 16:9 for YouTube on request.

## Font
- Figtree for all video text (headlines, numbers, captions). Weights: 800 headlines/numbers, 700 captions, 500-600 sub-lines. Bebas Neue and Inter are kept only for reference.

## Status
- Font decided: Figtree. Layout/color still open: website navy (A) or Instagram footage look (C). Decide on the first finished video.

## Style samples (Nov 24, 2026, for comparison; not yet chosen)
- render/styles/watercolor.py: watercolor field journal, washes bleed in on paper, hand-inked lines. Figtree.
- render/styles/luxury.py: quiet luxury, off-white and stone, Figtree light, slow push-in, lots of empty space.
- render/styles/clean3d.py: clean 3D render, minimal court rotates while parts get labeled (turf, sand infill, glass, mesh, lights). Figtree.
- render/styles/hybrid.py: real footage on watercolor paper; freeze frames get ink circles, arrows, yellow highlights; numbers cut to a quick watercolor chart.
- render/styles/polaroid.py: instant-film scrapbook, Polaroids drop onto corkboard with a bounce, slow pan.
- Vox paper collage: Raj asked for it again as an option (Nov 24); renderer lives in git history (57f0575).
- render/styles/illustrated.py: grainy illustrated landscape (sunset sky, layered hills, cypress, brush texture), court plan on a backyard lawn. Inspired by the look of Raj's reference cards, original artwork, no logos.
- Chosen for the dimensions video: illustrated, terracotta turf (Raj, Nov 24; replaces clean 3D). Key frames: render/styles/dims_illustrated.py. Overhead still: render/styles/illustrated_overhead.py.
- No "American Padel Labs" text at the top of frames (Raj, Nov 24).
- Motion notes from Raj's three reference loops (Nov 24): short living loops (3 to 6 s), slow push-in, gentle parallax, small ambient motion (birds, drifting clouds, swaying trees, sun glow), saturated sunset palette, visible brush grain. Applied to illustrated.py.

## Formats and safe zones (Nov 24, 2026)
Every still/video is made in four formats by render/styles/pages_fmt.py (FMT=reel|feed|square|wide):
- reel 1080x1920 (Instagram Reels/Stories, TikTok, YouTube Shorts): text only inside x 65-960, y 270-1248 (Meta Ads Guide margins: top 270, bottom 672, sides 65, right rail 120). Caption block sits at the top.
- feed 1080x1350 (Instagram/LinkedIn feed): 60 px margins, title top, caption bottom.
- square 1080x1080: 60 px margins, title top, caption bottom.
- wide 1920x1080 (YouTube, LinkedIn, X): 96/60 px margins, text column on the left, court on the right.
No text panels: white text with a soft shadow straight on the scene. One key takeaway per page.
