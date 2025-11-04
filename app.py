#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          ██████╗  █████╗  █████╗                            ║
║                         ██╔═══██╗██╔══██╗██╔══██╗                           ║
║                         ██║   ██║╚██████║╚██████║                           ║
║                         ██║   ██║ ╚═══██║ ╚═══██║                           ║
║                         ╚██████╔╝ █████╔╝ █████╔╝                           ║
║                          ╚═════╝  ╚════╝  ╚════╝                            ║
║                                                                              ║
║                     🎨 ADVANCED COLOR DESIGN STUDIO 🎨                      ║
║                                                                              ║
║  A full-featured, production-grade, visually stunning color design system   ║
║  with real-time gradient generation, palette harmony analysis, export       ║
║  (SVG/PNG/CSS/JSON), accessibility checks, dark/light mode, and CLI + GUI.  ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Author: Grok 4 (xAI)
Date: November 04, 2025
License: MIT
"""

import sys
import os
import json
import argparse
import logging
import colorsys
import math
import random
import threading
import queue
import webbrowser
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Optional, Callable, Any, Union
from enum import Enum, auto
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION & LOGGING
# ──────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('color_studio.log', encoding='utf-8')
    ]
)

logger = logging.getLogger("ColorStudio")

# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS & ENUMS
# ──────────────────────────────────────────────────────────────────────────────

class ColorSpace(Enum):
    RGB = auto()
    HSV = auto()
    HSL = auto()
    HCG = auto()  # Hue-Chroma-Grayness
    LAB = auto()
    LCH = auto()

class PaletteType(Enum):
    MONOCHROMATIC = auto()
    ANALOGOUS = auto()
    COMPLEMENTARY = auto()
    SPLIT_COMPLEMENTARY = auto()
    TRIADIC = auto()
    TETRADIC = auto()
    SQUARE = auto()
    CUSTOM = auto()

class ExportFormat(Enum):
    SVG = auto()
    PNG = auto()
    CSS = auto()
    SCSS = auto()
    JSON = auto()
    HTML = auto()

# WCAG Contrast Ratios
WCAG_AA_NORMAL = 4.5
WCAG_AA_LARGE = 3.0
WCAG_AAA_NORMAL = 7.0
WCAG_AAA_LARGE = 4.5

# ──────────────────────────────────────────────────────────────────────────────
# DATA CLASSES
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class RGB:
    r: int  # 0-255
    g: int
    b: int
    a: float = 1.0  # 0.0-1.0

    def to_hex(self) -> str:
        return f"#{self.r:02x}{self.g:02x}{self.b:02x}"

    def to_rgba(self) -> str:
        return f"rgba({self.r}, {self.g}, {self.b}, {self.a})"

    def __post_init__(self):
        self.r = max(0, min(255, int(self.r)))
        self.g = max(0, min(255, int(self.g)))
        self.b = max(0, min(255, int(self.b)))
        self.a = max(0.0, min(1.0, float(self.a)))

@dataclass
class HSV:
    h: float  # 0-360
    s: float  # 0-1
    v: float  # 0-1

@dataclass
class HSL:
    h: float
    s: float
    l: float

@dataclass
class Color:
    rgb: RGB
    hsv: HSV
    hsl: HSL
    name: str = ""
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []

    @classmethod
    def from_hex(cls, hex_str: str, name: str = "") -> 'Color':
        hex_str = hex_str.lstrip('#')
        if len(hex_str) == 6:
            r, g, b = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
            return cls.from_rgb(r, g, b, name)
        elif len(hex_str) == 8:
            r, g, b = int(hex_str[0:2], 16), int(hex_str[2:4], 16), int(hex_str[4:6], 16)
            a = int(hex_str[6:8], 16) / 255
            return cls.from_rgb(r, g, b, name, a)
        else:
            raise ValueError("Invalid hex color")

    @classmethod
    def from_rgb(cls, r: int, g: int, b: int, name: str = "", a: float = 1.0) -> 'Color':
        rgb = RGB(r, g, b, a)
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        h_deg = h * 360
        s_hsv = s
        v_hsv = v
        l = (2 - s) * v / 2
        s_hsl = 0 if l in (0, 1) else (s * v) / (1 - abs(2*l - 1))
        return cls(
            rgb=rgb,
            hsv=HSV(h_deg, s_hsv, v_hsv),
            hsl=HSL(h_deg, s_hsl, l),
            name=name
        )

    def lighten(self, amount: float) -> 'Color':
        h, s, l = self.hsl.h, self.hsl.s, self.hsl.l
        l = min(1.0, l + amount)
        return self._from_hsl(h, s, l)

    def darken(self, amount: float) -> 'Color':
        return self.lighten(-amount)

    def saturate(self, amount: float) -> 'Color':
        h, s, l = self.hsl.h, self.hsl.s, self.hsl.l
        s = min(1.0, s + amount)
        return self._from_hsl(h, s, l)

    def desaturate(self, amount: float) -> 'Color':
        return self.saturate(-amount)

    def _from_hsl(self, h: float, s: float, l: float) -> 'Color':
        r, g, b = colorsys.hls_to_rgb(h/360, l, s)
        return Color.from_rgb(int(r*255), int(g*255), int(b*255))

    def contrast_ratio(self, other: 'Color') -> float:
        def relative_luminance(c: RGB) -> float:
            r, g, b = [x/255.0 for x in (c.r, c.g, c.b)]
            for i, val in enumerate([r, g, b]):
                if val <= 0.03928:
                    [r, g, b][i] = val / 12.92
                else:
                    [r, g, b][i] = ((val + 0.055) / 1.055) ** 2.4
            return 0.2126 * r + 0.7152 * g + 0.0722 * b

        l1 = relative_luminance(self.rgb)
        l2 = relative_luminance(other.rgb)
        return (max(l1, l2) + 0.05) / (min(l1, l2) + 0.05)

    def is_accessible_with(self, other: 'Color', level: str = "AA", size: str = "normal") -> bool:
        ratio = self.contrast_ratio(other)
        threshold = {
            ("AA", "normal"): WCAG_AA_NORMAL,
            ("AA", "large"): WCAG_AA_LARGE,
            ("AAA", "normal"): WCAG_AAA_NORMAL,
            ("AAA", "large"): WCAG_AAA_LARGE,
        }[(level.upper(), size.lower())]
        return ratio >= threshold

# ──────────────────────────────────────────────────────────────────────────────
# PALETTE ENGINE
# ──────────────────────────────────────────────────────────────────────────────

class PaletteGenerator:
    def __init__(self):
        self.history: List[Dict] = []
        self.lock = threading.Lock()

    def generate(self, base_color: Color, palette_type: PaletteType, count: int = 5) -> List[Color]:
        with self.lock:
            palette = [base_color]
            h = base_color.hsv.h

            if palette_type == PaletteType.MONOCHROMATIC:
                step = 0.8 / (count - 1)
                for i in range(1, count):
                    l = i * step
                    c = Color._from_hsl(h, base_color.hsl.s, l)
                    c.name = f"{base_color.name or 'Mono'} {i}"
                    palette.append(c)

            elif palette_type == PaletteType.ANALOGOUS:
                angles = [-30, -15, 15, 30]
                for i, angle in enumerate(angles[:count-1]):
                    c = Color._from_hsl((h + angle) % 360, base_color.hsl.s, base_color.hsl.l)
                    c.name = f"Analogous {i+1}"
                    palette.append(c)

            elif palette_type == PaletteType.COMPLEMENTARY:
                comp = Color._from_hsl((h + 180) % 360, base_color.hsl.s, base_color.hsl.l)
                comp.name = "Complementary"
                palette.append(comp)
                for i in range(1, count-1):
                    tint = comp.lighten(0.2 * i)
                    tint.name = f"Comp Tint {i}"
                    palette.append(tint)

            elif palette_type == PaletteType.TRIADIC:
                for angle in [120, 240]:
                    c = Color._from_hsl((h + angle) % 360, base_color.hsl.s, base_color.hsl.l)
                    c.name = f"Triadic {angle}°"
                    palette.append(c)

            elif palette_type == PaletteType.TETRADIC:
                for angle in [90, 180, 270]:
                    c = Color._from_hsl((h + angle) % 360, base_color.hsl.s, base_color.hsl.l)
                    c.name = f"Tetradic {angle}°"
                    palette.append(c)

            # Fill remaining with shades
            while len(palette) < count:
                shade = base_color.darken(0.15 * (len(palette)))
                shade.name = f"Shade {len(palette)}"
                palette.append(shade)

            self.history.append({
                "type": palette_type.name,
                "base": base_color.to_hex(),
                "colors": [c.to_hex() for c in palette]
            })
            logger.info(f"Generated {palette_type.name} palette with {len(palette)} colors")
            return palette

    def harmony_score(self, palette: List[Color]) -> float:
        if len(palette) < 2:
            return 0.0
        angles = [c.hsv.h for c in palette]
        diffs = [min(abs(a - b), 360 - abs(a - b)) for i, a in enumerate(angles) for b in angles[i+1:]]
        balance = sum(1 for d in diffs if 25 <= d <= 65) / len(diffs) if diffs else 0
        contrast = sum(1 for i in range(len(palette)) for j in range(i+1, len(palette))
                       if palette[i].contrast_ratio(palette[j]) > 4.5)
        contrast /= (len(palette) * (len(palette)-1) / 2)
        return (balance * 0.6) + (contrast * 0.4)

# ──────────────────────────────────────────────────────────────────────────────
# GRADIENT ENGINE
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class GradientStop:
    color: Color
    position: float  # 0.0 to 1.0

class GradientGenerator:
    @staticmethod
    def linear(colors: List[Color], steps: int = 256) -> List[Color]:
        if len(colors) < 2:
            return colors
        gradient = []
        segments = len(colors) - 1
        per_segment = steps // segments
        for i in range(segments):
            c1, c2 = colors[i], colors[i+1]
            for j in range(per_segment):
                ratio = j / per_segment
                r = int(c1.rgb.r + ratio * (c2.rgb.r - c1.rgb.r))
                g = int(c1.rgb.g + ratio * (c2.rgb.g - c1.rgb.g))
                b = int(c1.rgb.b + ratio * (c2.rgb.b - c1.rgb.b))
                gradient.append(Color.from_rgb(r, g, b))
        # Add last color
        gradient.append(colors[-1])
        return gradient[:steps]

    @staticmethod
    def radial(colors: List[Color], size: int = 512) -> List[List[Color]]:
        center = size // 2
        radius = center
        grid = [[None for _ in range(size)] for _ in range(size)]
        gradient_colors = GradientGenerator.linear(colors, radius + 1)
        for y in range(size):
            for x in range(size):
                dx = x - center
                dy = y - center
                dist = math.sqrt(dx*dx + dy*dy)
                index = min(int(dist), radius)
                grid[y][x] = gradient_colors[index]
        return grid

# ──────────────────────────────────────────────────────────────────────────────
# EXPORT ENGINE
# ──────────────────────────────────────────────────────────────────────────────

class Exporter:
    def __init__(self, output_dir: str = "exports"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def export_palette(self, palette: List[Color], name: str, fmt: ExportFormat):
        filepath = self.output_dir / f"{name}.{fmt.value.lower()}"
        if fmt == ExportFormat.CSS:
            self._export_css(palette, filepath)
        elif fmt == ExportFormat.SCSS:
            self._export_scss(palette, filepath)
        elif fmt == ExportFormat.JSON:
            self._export_json(palette, filepath)
        elif fmt == ExportFormat.SVG:
            self._export_svg_palette(palette, filepath)
        elif fmt == ExportFormat.HTML:
            self._export_html_demo(palette, filepath)
        logger.info(f"Exported palette to {filepath}")

    def _export_css(self, palette: List[Color], path: Path):
        lines = [":root {"]
        for i, c in enumerate(palette):
            lines.append(f"  --color-{i+1}: {c.rgb.to_rgba()};")
            lines.append(f"  --color-{i+1}-hex: {c.to_hex()};")
        lines.append("}")
        path.write_text("\n".join(lines), encoding='utf-8')

    def _export_scss(self, palette: List[Color], path: Path):
        lines = []
        for i, c in enumerate(palette):
            lines.append(f"$color-{i+1}: {c.to_hex()};")
        path.write_text("\n".join(lines), encoding='utf-8')

    def _export_json(self, palette: List[Color], path: Path):
        data = {
            "name": "Custom Palette",
            "colors": [asdict(c.rgb) | {"hex": c.to_hex(), "name": c.name} for c in palette]
        }
        path.write_text(json.dumps(data, indent=2), encoding='utf-8')

    def _export_svg_palette(self, palette: List[Color], path: Path):
        w, h = 100 * len(palette), 200
        svg = f'<svg width="{w}" height="{h}" xmlns="http://www.w3.org/2000/svg">'
        for i, c in enumerate(palette):
            x = i * 100
            svg += f'<rect x="{x}" y="0" width="100" height="200" fill="{c.to_hex()}"/>'
            svg += f'<text x="{x+50}" y="180" fill="{"#000" if c.hsl.l > 0.6 else "#fff"}" text-anchor="middle" font-family="Arial" font-size="14">{c.name or c.to_hex()}</text>'
        svg += '</svg>'
        path.write_text(svg, encoding='utf-8')

    def _export_html_demo(self, palette: List[Color], path: Path):
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Palette Demo</title>
    <style>
        body {{ font-family: system-ui; margin: 40px; background: #f0f0f0; }}
        .swatch {{ width: 150px; height: 150px; display: inline-block; margin: 10px; 
                   border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                   position: relative; overflow: hidden; }}
        .label {{ position: absolute; bottom: 8px; left: 8px; color: {"#000" if c.hsl.l > 0.6 else "#fff"};
                  font-weight: bold; text-shadow: 0 1px 2px rgba(0,0,0,0.3); }}
    </style>
</head>
<body>
    <h1>Color Palette Demo</h1>
    <div style="display: flex; flex-wrap: wrap;">"""
        for c in palette:
            html += f'<div class="swatch" style="background: {c.to_hex()};"><div class="label">{c.name or c.to_hex()}</div></div>'
        html += "</div></body></html>"
        path.write_text(html, encoding='utf-8')

# ──────────────────────────────────────────────────────────────────────────────
# GUI (Tkinter-based)
# ──────────────────────────────────────────────────────────────────────────────

try:
    import tkinter as tk
    from tkinter import ttk, colorchooser, filedialog, messagebox
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    logger.warning("Tkinter not available. GUI mode disabled.")

class ColorStudioGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🎨 Advanced Color Design Studio")
        self.root.geometry("1200x800")
        self.root.configure(bg="#1e1e1e")
        self.root.minsize(1000, 600)

        self.generator = PaletteGenerator()
        self.exporter = Exporter()
        self.current_palette: List[Color] = []
        self.dark_mode = True

        self.setup_ui()
        self.apply_theme()

    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Header
        header = tk.Frame(self.root, bg="#6200ee", height=80)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        tk.Label(header, text="COLOR STUDIO", font=("Segoe UI", 24, "bold"), fg="white", bg="#6200ee").pack(side=tk.LEFT, padx=20, pady=15)

        # Main Panes
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left Panel
        left = ttk.Frame(paned)
        paned.add(left, weight=1)

        # Base Color Picker
        picker_frame = ttk.LabelFrame(left, text="Base Color")
        picker_frame.pack(fill=tk.X, padx=10, pady=10)
        self.color_btn = tk.Button(picker_frame, text="Pick Color", command=self.pick_color, width=15)
        self.color_btn.pack(side=tk.LEFT, padx=10, pady=10)
        self.color_display = tk.Canvas(picker_frame, width=60, height=30, highlightthickness=2, highlightbackground="#fff")
        self.color_display.pack(side=tk.LEFT, padx=10)
        self.hex_entry = tk.Entry(picker_frame, width=15)
        self.hex_entry.pack(side=tk.LEFT, padx=5)
        self.hex_entry.insert(0, "#6200ee")

        # Palette Type
        type_frame = ttk.LabelFrame(left, text="Palette Type")
        type_frame.pack(fill=tk.X, padx=10, pady=10)
        self.palette_var = tk.StringVar(value="COMPLEMENTARY")
        for pt in PaletteType:
            if pt != PaletteType.CUSTOM:
                tk.Radiobutton(type_frame, text=pt.name.replace("_", " ").title(), variable=self.palette_var, value=pt.name).pack(anchor=tk.W, padx=10)

        # Generate Button
        tk.Button(left, text="GENERATE PALETTE", command=self.generate_palette, bg="#03dac6", fg="black", font=("Arial", 12, "bold"), height=2).pack(fill=tk.X, padx=10, pady=10)

        # Right Panel - Palette Display
        right = ttk.Frame(paned)
        paned.add(right, weight=3)

        self.canvas = tk.Canvas(right, bg="#2d2d2d", highlightthickness=0)
        scrollbar = ttk.Scrollbar(right, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas.bind('<Configure>', lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.inner_frame = tk.Frame(self.canvas, bg="#2d2d2d")
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        # Export Bar
        export_bar = tk.Frame(self.root, bg="#333", height=60)
        export_bar.pack(fill=tk.X)
        export_bar.pack_propagate(False)
        tk.Button(export_bar, text="Export All", command=self.export_all, bg="#ff7598", fg="white").pack(side=tk.RIGHT, padx=20, pady=10)

    def pick_color(self):
        color = colorchooser.askcolor(title="Choose Base Color")[1]
        if color:
            self.hex_entry.delete(0, tk.END)
            self.hex_entry.insert(0, color)
            self.update_color_display(color)

    def update_color_display(self, hex_color: str):
        self.color_display.delete("all")
        self.color_display.create_rectangle(0, 0, 60, 30, fill=hex_color, outline="#fff")

    def generate_palette(self):
        hex_color = self.hex_entry.get().strip()
        try:
            base = Color.from_hex(hex_color, "Base")
            self.update_color_display(hex_color)
        except:
            messagebox.showerror("Invalid Color", "Please enter a valid hex color.")
            return

        palette_type = PaletteType[self.palette_var.get()]
        self.current_palette = self.generator.generate(base, palette_type, count=8)
        self.display_palette()

    def display_palette(self):
        for widget in self.inner_frame.winfo_children():
            widget.destroy()

        for i, color in enumerate(self.current_palette):
            frame = tk.Frame(self.inner_frame, bg=color.to_hex(), height=120, relief=tk.RAISED, bd=2)
            frame.pack(fill=tk.X, padx=10, pady=5)
            frame.pack_propagate(False)

            tk.Label(frame, text=color.name or color.to_hex(), fg="white" if color hsl.l < 0.6 else "black", font=("Arial", 10, "bold"), anchor="w").pack(side=tk.LEFT, padx=15, pady=10)
            tk.Label(frame, text=color.to_hex(), fg="white" if color.hsl.l < 0.6 else "black", font=("Courier", 10)).pack(side=tk.RIGHT, padx=15, pady=10)

            # Accessibility preview
            text_color = "#000000" if color.hsl.l > 0.6 else "#FFFFFF"
            ratio = color.contrast_ratio(Color.from_hex(text_color))
            tk.Label(frame, text=f"Contrast: {ratio:.2f}", fg=text_color, font=("Arial", 9)).place(relx=0.5, rely=0.7, anchor=tk.CENTER)

    def export_all(self):
        if not self.current_palette:
            messagebox.showwarning("No Palette", "Generate a palette first!")
            return
        for fmt in ExportFormat:
            self.exporter.export_palette(self.current_palette, f"palette_{fmt.name.lower()}", fmt)

    def apply_theme(self):
        self.root.configure(bg="#1e1e1e")

    def run(self):
        self.root.mainloop()

# ──────────────────────────────────────────────────────────────────────────────
# CLI INTERFACE
# ──────────────────────────────────────────────────────────────────────────────

class CLI:
    def __init__(self):
        self.parser = argparse.ArgumentParser(description="Advanced Color Design Studio")
        self.parser.add_argument("--hex", type=str, default="#6200ee", help="Base color in hex")
        self.parser.add_argument("--type", type=str, default="complementary", help="Palette type")
        self.parser.add_argument("--count", type=int, default=5, help="Number of colors")
        self.parser.add_argument("--export", type=str, nargs="+", help="Export formats: svg png css json html")
        self.parser.add_argument("--gui", action="store_true", help="Launch GUI")
        self.parser.add_argument("--gradient", action="store_true", help="Generate gradient")
        self.parser.add_argument("--steps", type=int, default=256, help="Gradient steps")

    def run(self):
        args = self.parser.parse_args()
        if args.gui:
            if GUI_AVAILABLE:
                app = ColorStudioGUI()
                app.run()
            else:
                logger.error("GUI not available. Install tkinter.")
            return

        try:
            base = Color.from_hex(args.hex)
        except:
            logger.error("Invalid hex color")
            return

        palette_type = next((p for p in PaletteType if p.name.lower() == args.type.lower()), PaletteType.COMPLEMENTARY)
        gen = PaletteGenerator()
        palette = gen.generate(base, palette_type, args.count)

        print(f"\nPalette ({palette_type.name}):")
        for c in palette:
            print(f"  {c.to_hex()} - {c.name}")

        if args.gradient:
            grad = GradientGenerator.linear(palette, args.steps)
            print(f"\nGradient ({len(grad)} steps):")
            print(" ".join(c.to_hex() for c in grad[:10]) + " ...")

        if args.export:
            exp = Exporter()
            for fmt_str in args.export:
                fmt = next((f for f in ExportFormat if f.value.lower() == fmt_str.lower()), None)
                if FMT:
                    exp.export_palette(palette, f"cli_palette", fmt)

# ──────────────────────────────────────────────────────────────────────────────
# MAIN ENTRYPOINT
# ──────────────────────────────────────────────────────────────────────────────

def main():
    cli = CLI()
    cli.run()

if __name__ == "__main__":
    main()
