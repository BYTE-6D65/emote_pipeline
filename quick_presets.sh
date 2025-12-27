#!/bin/bash
# Quick presets for common emote generation workflows

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PIPELINE="$SCRIPT_DIR/emote_pipeline.py"

show_help() {
    cat << EOF
Quick Presets for Emote Pipeline

Usage: $0 <preset> <input.png> [output-name]

Presets:
  web          - General web use (1000x1000, white outline, 10MB max)
  discord      - Discord standard (512x512, 3px outline, 256KB max)
  discord-hd   - Discord HD (1000x1000, 6px outline, 10MB max)
  twitch       - Twitch emote (112x112, 3px outline, 1MB max)
  small        - Small emote (256x256, 4px outline, 1MB max)
  high-quality - High-quality APNG (2000x2000, 12px outline, no GIF)

Examples:
  $0 web tail.png
  $0 discord tail.png my_discord_emote.gif
  $0 high-quality tail.png hq_output.png

EOF
}

if [ $# -lt 2 ]; then
    show_help
    exit 1
fi

PRESET="$1"
INPUT="$2"
OUTPUT="${3:-}"

# Default output name based on preset
if [ -z "$OUTPUT" ]; then
    BASENAME=$(basename "$INPUT" .png)
    OUTPUT="${BASENAME}_${PRESET}.gif"
fi

case "$PRESET" in
    web)
        echo "🌐 Generating web emote (1000x1000, white outline, 10MB max)..."
        python3 "$PIPELINE" -i "$INPUT" -o "$OUTPUT" \
            -s 1000 -w 6.0 --max-size 10.0
        ;;

    discord)
        echo "💬 Generating Discord emote (512x512, 3px outline, 256KB max)..."
        python3 "$PIPELINE" -i "$INPUT" -o "$OUTPUT" \
            -s 512 -w 3.0 --max-size 0.25
        ;;

    discord-hd)
        echo "💬 Generating Discord HD emote (1000x1000, 6px outline, 10MB max)..."
        python3 "$PIPELINE" -i "$INPUT" -o "$OUTPUT" \
            -s 1000 -w 6.0 --max-size 10.0
        ;;

    twitch)
        echo "📺 Generating Twitch emote (112x112, 3px outline, 1MB max)..."
        python3 "$PIPELINE" -i "$INPUT" -o "$OUTPUT" \
            -s 112 -w 3.0 --max-size 1.0
        ;;

    small)
        echo "🔹 Generating small emote (256x256, 4px outline, 1MB max)..."
        python3 "$PIPELINE" -i "$INPUT" -o "$OUTPUT" \
            -s 256 -w 4.0 --max-size 1.0
        ;;

    high-quality)
        # For high-quality, output should be .png
        if [[ "$OUTPUT" == *.gif ]]; then
            OUTPUT="${OUTPUT%.gif}.png"
        fi
        echo "✨ Generating high-quality APNG (2000x2000, 12px outline, no compression)..."
        python3 "$PIPELINE" -i "$INPUT" -o "$OUTPUT" \
            -s 2000 -w 12.0 --skip-gif
        ;;

    *)
        echo "❌ Unknown preset: $PRESET"
        echo ""
        show_help
        exit 1
        ;;
esac

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Complete! Output: $OUTPUT"
else
    echo ""
    echo "❌ Pipeline failed"
    exit 1
fi
