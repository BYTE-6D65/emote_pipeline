# Argument Standards

All scripts in this pipeline follow the same argument conventions.

## Universal Pattern

```bash
python3 {script}.py -i INPUT -o OUTPUT [OPTIONS]
```

## Required Arguments (Always First)

- `-i, --input` - Input file path
- `-o, --output` - Output file path

## Standard Options (Consistent Across Scripts)

### Size/Dimension Options
- `-s, --size` - Target size in pixels (square output)
- `--min-resolution` - Minimum required resolution

### Outline Options
- `-c, --color` - Outline color in hex RRGGBB (e.g., FFFFFF)
- `-w, --width` - Outline stroke width in pixels
- `--pad` - Padding around frames in pixels

### Quality/Compression Options
- `--max-size` - Maximum file size in MB
- `--alpha-threshold` - Alpha transparency threshold (0-255)

### Pipeline Control
- `--skip-outline` - Skip outline generation step
- `--skip-resize` - Skip resize step
- `--skip-gif` - Skip GIF conversion (output APNG)
- `--keep-temp` - Keep intermediate files
- `--temp-dir` - Custom temporary directory

## Script-Specific Quick Reference

### outline_gen.py
```bash
python3 outline_gen.py -i INPUT -o OUTPUT [OPTIONS]

Options:
  -s, --size SIZE          Target output size (default: input size)
  -c, --color COLOR        Outline color hex RRGGBB (default: FFFFFF)
  -w, --width WIDTH        Stroke width in pixels (default: 6.0)
  --pad PAD                Padding in pixels (default: 80)
```

### image_resize.py
```bash
python3 image_resize.py -i INPUT -o OUTPUT [OPTIONS]

Options:
  -s, --size SIZE          Target size in pixels (default: 1000)
```

### apng_to_gif.py
```bash
python3 apng_to_gif.py -i INPUT -o OUTPUT MAX_SIZE [OPTIONS]

Positional (legacy):
  MAX_SIZE                 Maximum size in MB

Options:
  --max-size SIZE          Maximum size in MB (alternative to positional)
  --alpha-threshold N      Alpha threshold 0-255 (default: 10)
  --min-resolution N       Minimum resolution required (default: 1000)
```

### emote_pipeline.py (Main Automation)
```bash
python3 emote_pipeline.py -i INPUT -o OUTPUT [OPTIONS]

Outline Options:
  -c, --color COLOR        Outline color (default: FFFFFF)
  -w, --width WIDTH        Stroke width (default: 6.0)
  --pad PAD                Padding (default: 80)

Resize Options:
  -s, --size SIZE          Target size (default: 1000)

GIF Options:
  --max-size SIZE          Max GIF size in MB (default: 10.0)

Pipeline Control:
  --skip-outline           Skip outline step
  --skip-resize            Skip resize step
  --skip-gif               Output APNG instead
  --keep-temp              Keep intermediate files
  --temp-dir DIR           Custom temp directory
```

## Examples

### Consistent Basic Usage
```bash
# All scripts follow the same -i/-o pattern
python3 outline_gen.py -i tail.png -o outlined.png
python3 image_resize.py -i outlined.png -o resized.png -s 1000
python3 apng_to_gif.py -i resized.png -o final.gif --max-size 10.0
```

### Using Short vs Long Forms (Both Supported)
```bash
# Short form
python3 emote_pipeline.py -i tail.png -o out.gif -c FFFFFF -w 6.0 -s 1000

# Long form (equivalent)
python3 emote_pipeline.py --input tail.png --output out.gif --color FFFFFF --width 6.0 --size 1000

# Mixed (also valid)
python3 emote_pipeline.py -i tail.png --output out.gif -c FFFFFF --width 6.0 -s 1000
```

### Advanced Options
```bash
# With all bells and whistles
python3 emote_pipeline.py \
  -i tail.png \
  -o final.gif \
  -c FF0000 \
  -w 8.0 \
  -s 2000 \
  --pad 100 \
  --max-size 5.0 \
  --keep-temp \
  --temp-dir ./debug
```

## Migration from Old Syntax

### Old (Inconsistent)
```bash
python3 apng_to_gif.py input.png 10.0 -o output.gif
python3 outline_gen.py --input in.png --output out.png --size 1000 -c FFFFFF
```

### New (Consistent)
```bash
python3 apng_to_gif.py -i input.png -o output.gif --max-size 10.0
python3 outline_gen.py -i in.png -o out.png -s 1000 -c FFFFFF
```

## Design Principles

1. **Required args first**: `-i` and `-o` always come first
2. **Both forms supported**: Short (`-w`) and long (`--width`) for all options
3. **Consistent naming**: Same option names across all scripts
4. **Logical grouping**: Related options documented together
5. **Sensible defaults**: All optional args have reasonable defaults
