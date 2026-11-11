# Si Juan Mulat

Faceless video para sa Facebook page na **Si Juan Mulat**.

**Episode 1: "Nasanay Na Tayo"** (1080x1920, 30fps, mga 1 minuto 55 segundo)

Ang bawat frame ay iginuguhit ng code sa `video.html`, kaya walang stock footage o larawang kailangang lisensyahan. Ang musika ay ginagawa rin ng code sa `music.py`.

## Paano i-build

Kailangan: Node na may Playwright at Chromium, Python 3 na may numpy, at ffmpeg.

```bash
./build.sh
```

Lalabas ang video sa `output/si-juan-mulat-ep1.mp4`.

## Paano baguhin

- **Mga salita at haba ng bawat eksena:** ang `SCENES` sa `video.html`. Ang `|` ang naghahati ng caption at ang `*ganito*` ang dilaw na salita.
- **Itsura ng eksena:** ang kaukulang function sa `S` (hal. `S.flood`).
- **Preview:** buksan ang `video.html` sa browser.

Walang voiceover ang video. Kung lalagyan ng boses, i-record ito sa ibabaw ng video sa CapCut at hinaan ang musika.
