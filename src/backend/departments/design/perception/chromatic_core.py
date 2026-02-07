# -*- coding: utf-8 -*-
"""
PROJECT: CHROMATIC SANCTUM (ห้องจิตภาพแห่งสี)
CONTEXT: AETHERIUM GENESIS / INSPIRAFIRMA
PURPOSE: ห้องทดลองผสมสีและจำลองฟิสิกส์ของพิกเซลสำหรับ AI
"""

import argparse
import json
import math
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Tuple, List

# --- 1. นิยามสเกลความลึกของสี (Bit Depth Definitions) ---
class BitDepth(Enum):
    BIT_1 = "1-bit"            # ขาว-ดำ (Thresholding)
    BIT_8_GRAY = "8-bit-gray"  # 256 ระดับสีเทา
    BIT_24_RGB = "24-bit-rgb"  # มาตรฐาน 16.7 ล้านสี
    BIT_32_PRO = "32-bit-pro"  # High Precision (จำลอง 10-12 bit ต่อ channel)

@dataclass
class SubPixel:
    """โครงสร้างซับพิกเซลทางฮาร์ดแวร์ (Red, Green, Blue)"""
    color: str
    intensity: int  # 0-255 (หรือมากกว่าใน 10-12 bit)

@dataclass
class PixelData:
    """หน่วยที่เล็กที่สุดของภาพดิจิทัล"""
    r: int
    g: int
    b: int
    bit_depth: str
    hex_code: str
    sub_pixels: List[dict]

# --- 2. แกนประมวลผลฟิสิกส์ (Physics Engine) ---
class ChromaticEngine:
    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self.count = 0
        # Simple buffer simulation
        self.particles = [None] * capacity

    def spawn(self, count):
        """
        Allocates particle slots safely.
        """
        # Validate and normalize count
        try:
            count = int(count)
        except (ValueError, TypeError):
            return []

        # Guard against non-positive values
        if count <= 0:
            return []

        # Compute spawn_count
        spawn_count = min(count, self.capacity - self.count)

        if spawn_count <= 0:
            return []

        idx = self.count
        end_idx = idx + spawn_count

        # Update state
        self.count += spawn_count

        # Return allocated indices (simulating the slice logic)
        return list(range(idx, end_idx))

    def _clamp(self, value, max_val=255):
        return max(0, min(value, max_val))

    def rgb_to_hex(self, r, g, b):
        """แปลงค่า RGB เป็นรหัส HEX ฐาน 16"""
        return "#{:02x}{:02x}{:02x}".format(self._clamp(r), self._clamp(g), self._clamp(b))

    def simulate_bit_depth(self, r, g, b, depth: BitDepth) -> Tuple[int, int, int]:
        """จำลองผลลัพธ์ของสีตามความลึกของบิต"""
        if depth == BitDepth.BIT_1:
            # คำนวณความสว่าง (Luminance) หากเกินครึ่งเป็นขาว ต่ำกว่าเป็นดำ
            lum = 0.299*r + 0.587*g + 0.114*b
            val = 255 if lum > 127 else 0
            return (val, val, val)

        elif depth == BitDepth.BIT_8_GRAY:
            # แปลงเป็น Grayscale ตามสูตรมาตรฐาน
            gray = int(0.299*r + 0.587*g + 0.114*b)
            return (gray, gray, gray)

        elif depth == BitDepth.BIT_24_RGB:
            # คืนค่าเดิม (Standard RGB)
            return (r, g, b)

        # สำหรับ 10-12 bit ใน Simulation นี้เราจะคืนค่า RGB ปกติ
        # แต่ในทางปฏิบัติจะรองรับค่า > 255
        return (r, g, b)

    def mix_light_additive(self, color1: Tuple[int,int,int], color2: Tuple[int,int,int]) -> Tuple[int,int,int]:
        """
        การผสมแสงแบบ Additive (เช่น จอภาพ): แสงรวมกันจะสว่างขึ้น
        Red + Green = Yellow, Red + Blue = Magenta, etc.
        """
        r = self._clamp(color1[0] + color2[0])
        g = self._clamp(color1[1] + color2[1])
        b = self._clamp(color1[2] + color2[2])
        return (r, g, b)

    def analyze_pixel(self, r, g, b, depth_str="24-bit-rgb"):
        """วิเคราะห์โครงสร้างพิกเซลและส่งคืนข้อมูลเชิงลึก"""
        try:
            depth = BitDepth(depth_str)
        except ValueError:
            depth = BitDepth.BIT_24_RGB

        # 1. Simulate Bit Depth Logic
        final_r, final_g, final_b = self.simulate_bit_depth(r, g, b, depth)

        # 2. Generate Hex
        hex_code = self.rgb_to_hex(final_r, final_g, final_b)

        # 3. Deconstruct to Sub-pixels (Hardware View)
        # จำลองการเรียงตัวของ Sub-pixel บนจอภาพ
        sub_pixels = [
            asdict(SubPixel("Red", final_r)),
            asdict(SubPixel("Green", final_g)),
            asdict(SubPixel("Blue", final_b))
        ]

        return PixelData(
            r=final_r,
            g=final_g,
            b=final_b,
            bit_depth=depth.value,
            hex_code=hex_code,
            sub_pixels=sub_pixels
        )

# --- 3. อินเทอร์เฟซรับคำสั่ง (CLI Entry Point) ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AETHERIUM GENESIS: Chromatic Sanctum Core")

    # Mode Selection
    parser.add_argument('--mode', type=str, required=True, choices=['analyze', 'mix'], help="Action mode")

    # Input for Analyze
    parser.add_argument('--rgb', nargs=3, type=int, help="RGB values like: 255 0 0")
    parser.add_argument('--depth', type=str, default="24-bit-rgb", help="Bit depth: 1-bit, 8-bit-gray, 24-bit-rgb")

    # Input for Mix
    parser.add_argument('--color1', nargs=3, type=int, help="RGB Color 1")
    parser.add_argument('--color2', nargs=3, type=int, help="RGB Color 2")

    args = parser.parse_args()
    engine = ChromaticEngine()
    result = {}

    if args.mode == 'analyze' and args.rgb:
        data = engine.analyze_pixel(args.rgb[0], args.rgb[1], args.rgb[2], args.depth)
        result = {
            "intent": "visualize_pixel_physics",
            "data": asdict(data),
            "description": f"Visualizing light intensity at {args.depth} scale."
        }

    elif args.mode == 'mix' and args.color1 and args.color2:
        mixed_rgb = engine.mix_light_additive(tuple(args.color1), tuple(args.color2))
        data = engine.analyze_pixel(mixed_rgb[0], mixed_rgb[1], mixed_rgb[2])
        result = {
            "intent": "additive_light_synthesis",
            "input_1": args.color1,
            "input_2": args.color2,
            "result_rgb": mixed_rgb,
            "result_hex": data.hex_code,
            "philosophy": "Light added to light creates brilliance."
        }

    # Output as JSON for the main AI system to consume
    print(json.dumps(result, indent=4, ensure_ascii=False))
