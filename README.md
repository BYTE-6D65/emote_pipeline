# Emote Pipeline

Automated pipeline for creating web-ready animated emotes with smooth vector outlines optimized for dark mode websites.

## Features

- ✅ **Vector outline generation** using potrace + Inkscape
- ✅ **High-quality resizing** with LANCZOS resampling
- ✅ **GIF optimization** with transparency preservation
- ✅ **Island handling** - No bridging between disconnected parts
- ✅ **Consistent CLI** - All scripts follow the same argument pattern
- ✅ **Platform presets** - Quick shortcuts for Discord, Twitch, etc.

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

### Method 1: Use Presets (Easiest)

```bash
# Web emote (1000x1000, 10MB)
./quick_presets.sh web tail.png

# Discord emote (512x512, 256KB)
./quick_presets.sh discord tail.png

# Twitch emote (112x112, 1MB)
./quick_presets.sh twitch tail.png
```

### Method 2: Full Control

```bash
# Basic - full pipeline with defaults
python3 emote_pipeline.py -i tail.png -o output.gif

# Custom settings
python3 emote_pipeline.py -i tail.png -o output.gif \
    -c FFFFFF -w 6.0 -s 1000 --max-size 10.0
```

## Standard Usage Pattern

**All scripts follow this consistent format:**

```bash
python3 {script}.py -i INPUT -o OUTPUT [OPTIONS]
```

Both short (`-w`) and long (`--width`) forms supported for all options.

## Main Pipeline

```bash
python3 emote_pipeline.py -i INPUT -o OUTPUT [OPTIONS]
```

### Options

**Outline:**
- `-c, --color COLOR` - Outline color in hex RRGGBB (default: FFFFFF)
- `-w, --width WIDTH` - Stroke width in pixels (default: 6.0)
- `--pad PAD` - Padding around frames prevents edge clipping (default: 80)

**Resize:**
- `-s, --size SIZE` - Target size in pixels, square (default: 1000)

**GIF:**
- `--max-size SIZE` - Maximum GIF size in MB (default: 10.0)

**Pipeline Control:**
- `--skip-outline` - Skip outline generation
- `--skip-resize` - Skip resize step
- `--skip-gif` - Output APNG instead of GIF
- `--keep-temp` - Keep intermediate files for debugging
- `--temp-dir DIR` - Custom temporary directory

### Examples

```bash
# Basic usage
python3 emote_pipeline.py -i tail.png -o web.gif

# Custom colored outline
python3 emote_pipeline.py -i tail.png -o red_outline.gif -c FF0000 -w 8.0

# Multiple platform outputs
python3 emote_pipeline.py -i tail.png -o web.gif -s 1000 --max-size 10.0
python3 emote_pipeline.py -i tail.png -o discord.gif -s 512 --max-size 0.25

# Debug mode (keep intermediate files)
python3 emote_pipeline.py -i tail.png -o output.gif --keep-temp
```

## Available Presets

| Preset | Size | Outline | Max Size | Use Case |
|--------|------|---------|----------|----------|
| `web` | 1000x1000 | 6px white | 10MB | General web/DMs |
| `discord` | 512x512 | 3px white | 256KB | Discord standard |
| `discord-hd` | 1000x1000 | 6px white | 10MB | Discord HD |
| `twitch` | 112x112 | 3px white | 1MB | Twitch emotes |
| `small` | 256x256 | 4px white | 1MB | Small emotes |
| `high-quality` | 2000x2000 | 12px white | N/A (APNG) | Source/editing |

```bash
./quick_presets.sh PRESET INPUT [OUTPUT]
```

## Common Workflows

### Create Web Emote from Procreate Export

```bash
# Export from Procreate as tail.png
./quick_presets.sh web tail.png web_emote.gif
```

### Create Multiple Sizes from One Source

```bash
# Generate all common sizes
./quick_presets.sh high-quality source.png source_hq.png
./quick_presets.sh web source_hq.png web.gif
./quick_presets.sh discord source_hq.png discord.gif
./quick_presets.sh twitch source_hq.png twitch.gif
```

### Already Have Outline? Skip That Step

```bash
python3 emote_pipeline.py -i outlined.png -o output.gif --skip-outline
```

## Individual Scripts

### 1. Outline Generation

```bash
python3 outline_gen.py -i INPUT -o OUTPUT [OPTIONS]
```

Options:
- `-s, --size SIZE` - Target size (default: input size)
- `-c, --color COLOR` - Outline color hex (default: FFFFFF)
- `-w, --width WIDTH` - Stroke width (default: 6.0)
- `--pad PAD` - Padding (default: 80)

Example:
```bash
python3 outline_gen.py -i input.png -o outlined.png -c FFFFFF -w 6.0
```

### 2. Image Resize

```bash
python3 image_resize.py -i INPUT -o OUTPUT [OPTIONS]
```

Options:
- `-s, --size SIZE` - Target size (default: 1000)

Example:
```bash
python3 image_resize.py -i outlined.png -o resized.png -s 1000
```

### 3. APNG to GIF

```bash
python3 apng_to_gif.py -i INPUT -o OUTPUT [OPTIONS]
```

Options:
- `--max-size SIZE` - Max size in MB (default: 10.0)
- `--alpha-threshold N` - Alpha threshold 0-255 (default: 10)
- `--min-resolution N` - Minimum input resolution enforced (rejects files smaller than this, default: 1000)

Example:
```bash
python3 apng_to_gif.py -i resized.png -o final.gif --max-size 10.0
```

## Pipeline Flow

```
┌─────────────┐
│ Input PNG   │
│ (Procreate) │
└──────┬──────┘
       │
       ▼
┌─────────────────────────┐
│ 1. Generate Outline     │
│ (outline_gen.py)        │
│ - Add padding           │
│ - Extract silhouette    │
│ - Vectorize with potrace│
│ - Apply stroke          │
│ - Composite             │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ 2. Resize               │
│ (image_resize.py)       │
│ - High-quality LANCZOS  │
│ - Square output         │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│ 3. Optimize GIF         │
│ (apng_to_gif.py)        │
│ - Convert to GIF        │
│ - Compress to target    │
│ - Preserve transparency │
└──────┬──────────────────┘
       │
       ▼
┌─────────────┐
│ Output GIF  │
│ (Web-ready) │
└─────────────┘
```

## Why This Order?

**❌ Wrong:** Resize → Outline → GIF
- Outline generated at low resolution = jagged edges
- Quality loss early in pipeline

**✅ Correct:** Outline → Resize → GIF
- Outline generated at full resolution = smooth vectors
- Single high-quality downsampling at end
- Can generate multiple sizes from one source

## Platform Limits Reference

### Discord
- **Standard emotes**: 256KB max
- **Recommended**: 128x128, 256x256, or 512x512
- **Animated**: GIF format

### Twitch
- **Emotes**: 1MB max
- **Sizes**: 28x28, 56x56, 112x112
- **Animated**: GIF format

### Slack/Teams
- **Typical**: 128KB limit
- **Recommended**: 128x128
- **Format**: GIF or PNG

### General Web
- **DM-friendly**: <10MB
- **Recommended**: 512x512 or 1000x1000
- **Format**: GIF or APNG

## Parameters Reference

### Outline Generation
- `-c, --color`: Hex color code (RRGGBB)
  - Examples: `FFFFFF` (white), `000000` (black), `FF0000` (red)
- `-w, --width`: Stroke width in pixels
  - Small emotes: 3.0-4.0
  - Large emotes: 6.0-12.0
  - **Note**: GIF conversion roughly doubles perceived outline thickness (e.g., `-w 3` looks like `-w 8` in final GIF)
- `--pad`: Padding around image
  - Default: 80px
  - Prevents outline clipping at edges

### Sizing
- `-s, --size`: Output dimensions (square)
  - Discord: 128, 256, 512
  - Twitch: 28, 56, 112
  - Web: 512, 1000, 2000

### GIF Optimization
- `--max-size`: Maximum file size in MB
  - Discord standard: 0.25 (256KB)
  - Twitch: 1.0
  - Web/DMs: 10.0

## Troubleshooting

### Problem: "potrace: command not found"
**Solution**: Install potrace
```bash
brew install potrace  # macOS
sudo apt-get install potrace  # Linux
```

### Problem: "inkscape: command not found"
**Solution**: Install Inkscape
```bash
brew install inkscape  # macOS
sudo apt-get install inkscape  # Linux
```

### Problem: Output file too large
**Solution**: Reduce `--max-size` or `-s` (dimensions)
```bash
python3 emote_pipeline.py -i input.png -o output.gif --max-size 5.0 -s 512
```

### Problem: Outline too thin/thick
**Solution**: Adjust `-w` parameter
```bash
# Thicker
python3 emote_pipeline.py -i input.png -o output.gif -w 10.0

# Thinner
python3 emote_pipeline.py -i input.png -o output.gif -w 3.0
```

### Problem: Want different color outline
**Solution**: Use `-c` with hex color
```bash
# Red
python3 emote_pipeline.py -i input.png -o output.gif -c FF0000

# Blue
python3 emote_pipeline.py -i input.png -o output.gif -c 0000FF

# Gray
python3 emote_pipeline.py -i input.png -o output.gif -c 808080
```

### Problem: Jagged outline in GIF
**Solution**: Pipeline generates outline at full resolution before resizing
- Use `--keep-temp` to inspect intermediate files

### Problem: Process is slow
**Expected**: ~70-110 seconds for 30-frame animation
- Outline generation: ~60-90s (vectorization is CPU intensive)
- Resize: ~5s
- GIF: ~5-15s

**Speedup options**:
- Reduce input resolution before processing
- Use `--pad 40` instead of 80
- Reduce `-w` (thinner outline = faster)

## Tips & Best Practices

1. **Start with high resolution** - Process at full resolution, then resize
2. **Use presets** - Fastest way for common platforms
3. **Keep high-quality source** - Use `high-quality` preset to save master copy
4. **Test outline width** - Try 3.0-12.0 range to find what looks best
5. **White outline for dark mode** - Creates maximum contrast on dark backgrounds
6. **Keep temp files for tweaking** - Use `--keep-temp` to iterate on settings

## Documentation

- [ARGUMENTS.md](ARGUMENTS.md) - Complete argument reference for all scripts

## Contributing

Issues and PRs welcome! Please ensure:
- All scripts follow standard argument pattern
- Both short and long forms work
- Documentation updated

## License

MIT

## Credits

- **potrace** - Bitmap to vector conversion
- **Inkscape** - SVG rasterization
- **Pillow** - Image processing
