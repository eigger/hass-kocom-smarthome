# Kocom Smart Home+ Energy brand assets

An original geometric smart wallpad and energy meter icon drawn by
`scripts/generate_brand.py` on a dark navy rounded square, with a matching cyan
`Kocom` wordmark for the landscape logo. They do not use the KOCOM logo or claim
to be official manufacturer artwork.

| File | Size | Purpose |
| --- | --- | --- |
| `icon.png` | 256 × 256 | Home Assistant and HACS icon |
| `icon@2x.png` | 512 × 512 | High-resolution icon |
| `logo.png` | 927 × 256 | Landscape integration logo; README artwork |
| `logo@2x.png` | 1854 × 512 | High-resolution landscape logo |

All images are RGBA PNGs with transparent outer corners and backgrounds. These
sizes follow the [HA brand image guidelines](https://contributors.home-assistant.io/core/integrations/brands/).
Home Assistant 2026.3 and later serves these assets from the integration's local
`brand/` directory. The cyan wordmark works against light and dark backgrounds,
so separate dark variants are not required.

## Source and permission

The icon is drawn from geometric primitives in this repository's
`scripts/generate_brand.py` and is covered by the repository's MIT license
(Copyright (c) 2026 eigger). The wordmark is rendered with Pillow's bundled
Aileron Regular via
[`ImageFont.load_default`](https://pillow.readthedocs.io/en/stable/reference/ImageFont.html#PIL.ImageFont.load_default).
[Aileron](https://dotcolon.net/font/aileron/) permits commercial use and is
released with no rights reserved. No font file is redistributed or loaded from
the system.

## Reproduce

Use Python 3.10 or newer and Pillow 12.3.0 (also supplied by HA 2026.10.2):

```sh
python -m pip install Pillow==12.3.0
python scripts/generate_brand.py
```

The script needs no network access and produces the same PNG bytes on every
run with that Pillow version.

SHA256 (Pillow 12.3.0):

- `icon@2x.png`: `464eae190a4174fc47df9812fc3e4f25c77efb57062beea938c1c41e24b29568`
- `icon.png`: `823f3cf1012231055d8a7b79b2d23af57fb30892fc1dd3bb4fb05b787b4e1e06`
- `logo@2x.png`: `b6bc24782acbe71f654db07571b6215ce0011b0791cf69423913a853e6c07397`
- `logo.png`: `6856e8868e46db8e446ab1b8be6dc1df7fa9c1b1e5689965721b333e5947efa7`

The local `brand/icon.png` is used by the
[HACS brands check](https://hacs.xyz/docs/publish/include/#check-brands).
These files do not imply inclusion in the HACS default list or HA brands
repository. README pages use `custom_components/kocom_smarthome/brand/logo.png`.
