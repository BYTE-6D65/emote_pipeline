# Emote Pipeline - Usage Guide

## Installation

```bash
# Install system dependencies
brew install potrace inkscape  # macOS
# OR
sudo apt-get install potrace inkscape  # Ubuntu/Debian

# Install Python dependencies
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

# High-quality APNG (2000x2000, no compression)
./quick_presets.sh high-quality tail.png
```

### Method 2: Full Control
```bash
# Basic - full pipeline with defaults
python3 emote_pipeline.py -i tail.png -o output.gif

# Custom settings
python3 emote_pipeline.py -i tail.png -o output.gif \\
    -c FFFFFF -w 6.0 -s 1000 --max-size 10.0
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

### Custom Colored Outline
```bash
# Red outline for visibility
python3 emote_pipeline.py -i tail.png -o red.gif -c FF0000 -w 8.0
```

### Already Have Outline? Skip That Step
```bash
python3 emote_pipeline.py -i outlined.png -o output.gif --skip-outline
```

### Debug Mode (Keep Intermediate Files)
```bash
python3 emote_pipeline.py -i tail.png -o output.gif --keep-temp
# Keeps: tail_outlined.png, tail_resized.png
```

## Parameters Reference

### Outline Generation
- `-c, --color`: Hex color code (RRGGBB)
  - Examples: `FFFFFF` (white), `000000` (black), `FF0000` (red)
- `-w, --width`: Stroke width in pixels
  - Typical: 3.0-12.0
  - Small emotes: 3.0-4.0
  - Large emotes: 6.0-12.0
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

### Pipeline Control
- `--skip-outline`: Input already has outline
- `--skip-resize`: Input already correct size
- `--skip-gif`: Output APNG instead of GIF
- `--keep-temp`: Don't delete intermediate files
- `--temp-dir`: Custom location for temp files

## Examples

### Example 1: Basic Web Emote
```bash
python3 emote_pipeline.py -i tail.png -o web.gif
```
**Result**: 1000x1000 GIF, white outline, <10MB

### Example 2: Discord Ready
```bash
./quick_presets.sh discord tail.png
```
**Result**: tail_discord.gif (512x512, <256KB)

### Example 3: Custom Black Outline
```bash
python3 emote_pipeline.py -i tail.png -o black_outline.gif \\
    -c 000000 -w 8.0
```
**Result**: 8px black outline instead of white

### Example 4: Multiple Outputs
```bash
# Create web and discord versions
python3 emote_pipeline.py -i tail.png -o web.gif -s 1000 --max-size 10.0
python3 emote_pipeline.py -i tail.png -o discord.gif -s 512 --max-size 0.25
```

### Example 5: Debug Workflow
```bash
# Keep intermediates for inspection
python3 emote_pipeline.py -i tail.png -o output.gif --keep-temp

# Check the files:
# - tail_outlined.png (after outline generation)
# - tail_resized.png (after resize)
# - output.gif (final)
```

## File Structure

```
flow_test/
├── emote_pipeline.py      # Main automation tool
├── quick_presets.sh       # Preset shortcuts
├── outline_gen.py         # Step 1: Vector outline
├── image_resize.py        # Step 2: Resize
├── apng_to_gif.py         # Step 3: GIF conversion
├── tail.png               # Example input
├── README.md              # Overview
└── USAGE.md               # This file
```

## Pipeline Diagram

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

### Problem: Process is slow
**Expected**: ~70-110 seconds for 30-frame animation
- Outline generation: ~60-90s (vectorization is CPU intensive)
- Resize: ~5s
- GIF: ~5-15s

**Speedup options**:
- Reduce input resolution before processing
- Use `--pad 40` instead of 80
- Reduce `-w` (thinner outline = faster)

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

## Tips & Best Practices

1. **Start with high resolution** - Process at full resolution, then resize
2. **Use presets** - Fastest way for common platforms
3. **Keep high-quality source** - Use `high-quality` preset to save master copy
4. **Test outline width** - Try 3.0-12.0 range to find what looks best
5. **White outline for dark mode** - Creates maximum contrast on dark backgrounds
6. **Keep temp files for tweaking** - Use `--keep-temp` to iterate on settings

## Next Steps

Once you have your emotes:

1. **Test on dark backgrounds** - Make sure outline provides good contrast
2. **Check file sizes** - Ensure they meet platform requirements
3. **Verify loop** - Check that animation loops smoothly
4. **Upload and enjoy!** 🎉
