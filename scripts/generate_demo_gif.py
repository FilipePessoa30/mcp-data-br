"""Gera `docs/assets/demo.gif` para o "30-second demo" do README.

Busca dados reais e atualizados de `comparar_municipios` (Rio de Janeiro,
Niterói e Maricá) chamando o `mcp-ibge` local via `demo_compare_municipios`,
e renderiza uma animação estilo terminal com efeito de digitação usando
Pillow — sem depender de ferramentas externas (VHS, ttyd, ffmpeg).

Uso:
    uv run --with pillow python scripts/generate_demo_gif.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from demo_compare_municipios import comparar_municipios_rj, format_table  # noqa: E402

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "docs" / "assets" / "demo.gif"

COMMAND = "uv run python scripts/demo_compare_municipios.py"
PROMPT = "$ "

# Tema (Catppuccin Mocha)
BG_COLOR = (30, 30, 46)
TITLEBAR_COLOR = (49, 50, 68)
DOT_COLORS = [(243, 139, 168), (249, 226, 175), (166, 227, 161)]
PROMPT_COLOR = (166, 227, 161)
TEXT_COLOR = (205, 214, 244)
DIM_COLOR = (147, 153, 178)
HIGHLIGHT_COLOR = (137, 220, 235)

FONT_SIZE = 20
PADDING = 20
TITLEBAR_HEIGHT = 36
LINE_SPACING = 1.4

FONT_CANDIDATES = [
    "C:/Windows/Fonts/CascadiaMono.ttf",
    "C:/Windows/Fonts/Consolas.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "/System/Library/Fonts/Menlo.ttc",
]


def load_font(size: int) -> ImageFont.ImageFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default(size=size)


Segment = tuple[str, tuple[int, int, int]]


def build_lines(table_lines: list[str]) -> list[list[Segment]]:
    """Monta as linhas finais do terminal como listas de (texto, cor)."""
    header, value_lines = table_lines[2], table_lines[3:]
    lines: list[list[Segment]] = [
        [(PROMPT, PROMPT_COLOR), (COMMAND, TEXT_COLOR)],
        [],
        [(table_lines[0], DIM_COLOR)],
        [],
        [(header, DIM_COLOR)],
    ]
    for row in value_lines:
        nome, resto = row[:16], row[16:]
        lines.append([(nome, HIGHLIGHT_COLOR), (resto, TEXT_COLOR)])
    return lines


def line_width(draw: ImageDraw.ImageDraw, segments: list[Segment], font: ImageFont.ImageFont) -> float:
    return sum(draw.textlength(text, font=font) for text, _ in segments)


def render_frame(
    visible_lines: list[list[Segment]],
    canvas_size: tuple[int, int],
    font: ImageFont.ImageFont,
    line_height: float,
    cursor: bool = False,
) -> Image.Image:
    image = Image.new("RGB", canvas_size, BG_COLOR)
    draw = ImageDraw.Draw(image)

    width, _height = canvas_size
    draw.rectangle([0, 0, width, TITLEBAR_HEIGHT], fill=TITLEBAR_COLOR)
    for i, color in enumerate(DOT_COLORS):
        cx = PADDING + i * 22
        draw.ellipse([cx, 12, cx + 12, 24], fill=color)
    title = "mcp-ibge — comparar municípios"
    draw.text((PADDING + 90, 9), title, font=font, fill=DIM_COLOR)

    for row, segments in enumerate(visible_lines):
        x = float(PADDING)
        y = TITLEBAR_HEIGHT + PADDING + row * line_height
        for text, color in segments:
            if text:
                draw.text((x, y), text, font=font, fill=color)
                x += draw.textlength(text, font=font)
        if cursor and row == 0:
            draw.rectangle([x, y + 2, x + draw.textlength("M", font=font), y + line_height - 2], fill=PROMPT_COLOR)

    return image


def main() -> None:
    envelope = asyncio.run(comparar_municipios_rj())
    table_lines = format_table(envelope)
    final_lines = build_lines(table_lines)

    font = load_font(FONT_SIZE)
    measure_image = Image.new("RGB", (10, 10))
    measure_draw = ImageDraw.Draw(measure_image)

    ascent, descent = font.getmetrics()
    line_height = (ascent + descent) * LINE_SPACING

    max_text_width = max(
        line_width(measure_draw, segments, font) for segments in final_lines if segments
    )
    canvas_width = int(max_text_width + PADDING * 2 + 10)
    canvas_height = int(TITLEBAR_HEIGHT + PADDING * 2 + len(final_lines) * line_height)
    canvas_size = (canvas_width, canvas_height)

    frames: list[Image.Image] = []
    durations: list[int] = []

    # 1) Efeito de digitação do comando.
    command_line = final_lines[0]
    for i in range(0, len(COMMAND) + 1, 2):
        partial = [(PROMPT, PROMPT_COLOR), (COMMAND[:i], TEXT_COLOR)]
        frames.append(render_frame([partial], canvas_size, font, line_height, cursor=True))
        durations.append(35)
    # Pequena pausa antes de "Enter".
    frames.append(render_frame([command_line], canvas_size, font, line_height, cursor=False))
    durations.append(300)

    # 2) Revela a saída do comando, uma linha por vez.
    for n in range(1, len(final_lines) + 1):
        frames.append(render_frame(final_lines[:n], canvas_size, font, line_height))
        durations.append(350)

    # 3) Mantém o resultado final na tela.
    durations[-1] = 3000

    palette_source = frames[-1].convert("P", palette=Image.ADAPTIVE, colors=64)
    frames_p = [f.quantize(palette=palette_source, dither=Image.Dither.NONE) for f in frames]

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    frames_p[0].save(
        OUTPUT_PATH,
        save_all=True,
        append_images=frames_p[1:],
        duration=durations,
        loop=0,
        optimize=True,
    )
    print(f"Gerado {OUTPUT_PATH} ({len(frames_p)} frames, {canvas_size[0]}x{canvas_size[1]})")


if __name__ == "__main__":
    main()
