# Emote Pipeline

Automated pipeline for creating web-ready animated emotes with smooth vector outlines.

## Features

- ✅ **Vector outline generation** using potrace + Inkscape
- ✅ **High-quality resizing** with LANCZOS resampling
- ✅ **GIF optimization** with transparency preservation
- ✅ **Island handling** - No bridging between disconnected parts
- ✅ **Consistent CLI** - All scripts follow the same argument pattern
- ✅ **Platform presets** - Quick shortcuts for Discord, Twitch, etc.

## Quick Start

```bash
# Install dependencies
brew install potrace inkscape  # macOS
pip install Pillow

# Run full pipeline
python3 emote_pipeline.py -i input.png -o output.gif

# Or use presets
./quick_presets.sh web input.png
./quick_presets.sh discord input.png
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
- `--pad PAD` - Padding around frames (default: 80)

**Resize:**
- `-s, --size SIZE` - Target size in pixels, square (default: 1000)

**GIF:**
- `--max-size SIZE` - Maximum GIF size in MB (default: 10.0)

**Pipeline Control:**
- `--skip-outline` - Skip outline generation
- `--skip-resize` - Skip resize step
- `--skip-gif` - Output APNG instead of GIF
- `--keep-temp` - Keep intermediate files
- `--temp-dir DIR` - Custom temporary directory

### Examples

```bash
# Basic usage
python3 emote_pipeline.py -i tail.png -o web.gif

# Custom settings
python3 emote_pipeline.py -i tail.png -o custom.gif \
  -c FF0000 -w 8.0 -s 2000 --max-size 5.0

# Debug mode
python3 emote_pipeline.py -i tail.png -o debug.gif --keep-temp
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
- `--min-resolution N` - Min resolution required (default: 1000)

Example:
```bash
python3 apng_to_gif.py -i resized.png -o final.gif --max-size 10.0
```

## Quick Presets

For common platforms:

```bash
./quick_presets.sh PRESET INPUT [OUTPUT]
```

Available presets:
- `web` - 1000x1000, white outline, 10MB
- `discord` - 512x512, 3px outline, 256KB
- `discord-hd` - 1000x1000, 6px outline, 10MB
- `twitch` - 112x112, 3px outline, 1MB
- `small` - 256x256, 4px outline, 1MB
- `high-quality` - 2000x2000, 12px outline, APNG

Examples:
```bash
./quick_presets.sh web tail.png
./quick_presets.sh discord tail.png my_emote.gif
```

## Pipeline Flow

```
Input PNG/APNG (native resolution)
    ↓
1. Generate vector outline at full resolution
   - Extract alpha mask
   - Vectorize with potrace --flat (handles islands)
   - Apply SVG stroke
   - Rasterize and composite
    ↓
2. Resize to target dimensions
   - High-quality LANCZOS downsampling
    ↓
3. Convert to optimized GIF
   - Preserve transparency
   - Compress to target size
    ↓
Output: Web-ready GIF
```

## Why This Order?

**❌ Wrong:** Resize → Outline → GIF
- Outline generated at low resolution = jagged edges
- Quality loss early in pipeline

**✅ Correct:** Outline → Resize → GIF
- Outline generated at full resolution = smooth vectors
- Single high-quality downsampling at end
- Can generate multiple sizes from one source

## Argument Standards

See [ARGUMENTS.md](ARGUMENTS.md) for complete argument documentation.

**Key principles:**
- `-i/--input` and `-o/--output` always required first
- Both short and long forms supported
- Consistent naming across all scripts
- Sensible defaults for all optional arguments

## Platform Targets

| Platform | Size | Max File Size | Preset |
|----------|------|---------------|--------|
| Discord Standard | 512x512 | 256KB | `discord` |
| Discord HD | 1000x1000 | 10MB | `discord-hd` |
| Twitch | 112x112 | 1MB | `twitch` |
| General Web | 1000x1000 | 10MB | `web` |

## Dependencies

### System Tools
```bash
# macOS
brew install potrace inkscape

# Ubuntu/Debian
sudo apt-get install potrace inkscape
```

### Python
```bash
pip install Pillow
```

## Troubleshooting

### Jagged outline in GIF
- Pipeline now generates outline at full resolution before resizing
- Use `--keep-temp` to inspect intermediate files

### Outline too thick/thin
- Adjust `-w/--width` (try 3.0-12.0)

### File too large
- Reduce `--max-size` or `-s/--size`

### "Command not found: potrace" or "inkscape"
- Install system dependencies (see Dependencies section)

### Outline doesn't align
- Fixed! Pipeline now preserves coordinate mapping

### Islands get bridged
- Fixed! Using `--flat` flag in potrace

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
