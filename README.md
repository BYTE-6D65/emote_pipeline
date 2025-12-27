# Emote Pipeline

Automated pipeline for creating web-ready animated emotes with smooth vector outlines optimized for dark mode websites.

## Example Output

<table>
<tr>
<td align="center"><strong>Input (APNG)</strong></td>
<td align="center"><strong>Output (GIF)</strong></td>
</tr>
<tr>
<td><img src="tail.png" width="300"></td>
<td><img src="tail.gif" width="300"></td>
</tr>
</table>

## Features

- Vector outline generation using potrace + Inkscape
- High-quality resizing with LANCZOS resampling
- GIF optimization with transparency preservation
- Island handling - no bridging between disconnected parts
- Platform presets for Discord, Twitch, and more

## Installation

```bash
# System dependencies
brew install potrace inkscape  # macOS
# OR
sudo apt-get install potrace inkscape  # Ubuntu/Debian

# Python dependencies
pip install Pillow
```

## Quick Start

### Presets (Easiest)

```bash
./quick_presets.sh web tail.png         # 1000x1000, 10MB
./quick_presets.sh discord tail.png     # 512x512, 256KB
./quick_presets.sh twitch tail.png      # 112x112, 1MB
```

### Full Pipeline

```bash
# Basic usage
python3 emote_pipeline.py -i tail.png -o output.gif

# Custom settings
python3 emote_pipeline.py -i tail.png -o output.gif \
    -c FFFFFF -w 6.0 -s 1000 --max-size 10.0
```

## Basic Usage

All scripts follow a consistent pattern:

```bash
python3 {script}.py -i INPUT -o OUTPUT [OPTIONS]
```

### Common Options

| Option | Description | Default |
|--------|-------------|---------|
| `-c, --color` | Outline color (hex RRGGBB) | FFFFFF |
| `-w, --width` | Stroke width (pixels) | 6.0 |
| `-s, --size` | Output size (pixels, square) | 1000 |
| `--max-size` | Max GIF file size (MB) | 10.0 |
| `--skip-outline` | Skip outline generation | - |
| `--keep-temp` | Keep intermediate files | - |

See [ARGUMENTS.md](ARGUMENTS.md) for complete option reference.

## Common Workflows

### Create Web Emote from Procreate Export

```bash
./quick_presets.sh web tail.png web_emote.gif
```

### Generate Multiple Sizes from One Source

```bash
./quick_presets.sh high-quality source.png source_hq.png
./quick_presets.sh web source_hq.png web.gif
./quick_presets.sh discord source_hq.png discord.gif
```

### Already Have Outline? Skip That Step

```bash
python3 emote_pipeline.py -i outlined.png -o output.gif --skip-outline
```

## Pipeline Flow

```
Input PNG (Procreate)
       |
       v
+---------------------------+
| 1. Generate Outline       |
| - Add padding             |
| - Extract silhouette      |
| - Vectorize with potrace  |
| - Apply stroke            |
+---------------------------+
       |
       v
+---------------------------+
| 2. Resize                 |
| - High-quality LANCZOS    |
| - Square output           |
+---------------------------+
       |
       v
+---------------------------+
| 3. Optimize GIF           |
| - Convert to GIF          |
| - Compress to target size |
| - Preserve transparency   |
+---------------------------+
       |
       v
  Output GIF (Web-ready)
```

## Platform Targets

| Preset | Size | Outline | Max Size | Use Case |
|--------|------|---------|----------|----------|
| `web` | 1000x1000 | 6px white | 10MB | General web/DMs |
| `discord` | 512x512 | 3px white | 256KB | Discord standard |
| `discord-hd` | 1000x1000 | 6px white | 10MB | Discord HD |
| `twitch` | 112x112 | 3px white | 1MB | Twitch emotes |
| `small` | 256x256 | 4px white | 1MB | Small emotes |
| `high-quality` | 2000x2000 | 12px white | N/A (APNG) | Source/editing |

## Key Concepts

### Why Outline at Full Resolution?

The pipeline generates outlines before resizing. This matters:

- **Wrong order** (Resize then Outline): Jagged edges from low-res vectorization
- **Correct order** (Outline then Resize): Smooth vectors downsampled once

### GIF Quirks

- Stroke width roughly doubles in perceived thickness after GIF conversion (e.g., `-w 3` looks like `-w 8` in final output)
- GIF only supports 1-bit transparency - semi-transparent pixels get thresholded
- Processing time is ~70-110 seconds for a 30-frame animation (vectorization is CPU intensive)

### White Outline for Dark Mode

Default white (`FFFFFF`) outline provides maximum contrast on dark backgrounds, which is the typical viewing context for emotes.

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `potrace: command not found` | `brew install potrace` (macOS) or `apt-get install potrace` (Linux) |
| `inkscape: command not found` | `brew install inkscape` (macOS) or `apt-get install inkscape` (Linux) |
| Output file too large | Reduce `--max-size` or `-s` (dimensions) |
| Outline too thin/thick | Adjust `-w` parameter (try 3.0-12.0 range) |
| Jagged outline in GIF | Use `--keep-temp` to inspect intermediate files |

## Documentation

- [ARGUMENTS.md](ARGUMENTS.md) - Complete argument reference for all scripts

## License

MIT

## Credits

- **potrace** - Bitmap to vector conversion
- **Inkscape** - SVG rasterization
- **Pillow** - Image processing
