# -*- coding: utf-8 -*-
"""
PROJECT: CHROMATIC SANCTUM INTERFACE
CONTEXT: AETHERIUM GENESIS / INSPIRAFIRMA
PURPOSE: Python wrapper for the Chromatic Sanctum micro-binary.
"""

import subprocess
import json
import os
import logging
from typing import Dict, Any, Tuple, Optional, Union

logger = logging.getLogger(__name__)

class ChromaticSanctum:
    """
    Interface for the Chromatic Sanctum micro-binary.
    This class handles the execution of the standalone binary to perform
    light physics calculations and pixel analysis.
    """

    def __init__(self, binary_path: Optional[str] = None):
        """
        Initialize the interface.

        Args:
            binary_path: Optional path to the binary. If not provided,
                         it assumes the binary is in the same directory as this file.
        """
        if binary_path:
            self.binary_path = binary_path
        else:
            # Default to the same directory as this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.binary_path = os.path.join(current_dir, "chromatic_core")

        self.available = True
        if not os.path.exists(self.binary_path):
            logger.warning(f"Chromatic Sanctum binary not found at: {self.binary_path}")
            self.available = False
        elif not os.access(self.binary_path, os.X_OK):
             logger.warning(f"Chromatic Sanctum binary is not executable: {self.binary_path}")
             self.available = False

        self.process: Optional[subprocess.Popen] = None

    def start(self):
        """
        Starts the persistent subprocess.
        """
        if not self.available:
            raise RuntimeError("Chromatic Sanctum binary is not available.")

        if self.process is not None:
            return

        try:
            self.process = subprocess.Popen(
                [self.binary_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
        except Exception as e:
            raise RuntimeError(f"Failed to start process: {e}")

    def stop(self):
        """
        Terminates the process and safely closes file descriptors to prevent leaks.
        """
        if self.process is None:
            return

        # 1. Terminate Logic
        try:
            self.process.terminate()
            try:
                self.process.wait(timeout=0.2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=0.2)
        except Exception:
            # Process might be already gone or permission denied
            pass
        finally:
            # 2. Explicit Pipe Cleanup
            pipes = [
                ('stdin', self.process.stdin),
                ('stdout', self.process.stdout),
                ('stderr', self.process.stderr)
            ]

            for name, pipe in pipes:
                if pipe is not None:
                    try:
                        pipe.close()
                    except (ValueError, OSError, BrokenPipeError):
                        pass

            # 3. Clear Reference
            self.process = None

    def _run_command(self, args: list) -> Dict[str, Any]:
        """
        Execute the binary with the given arguments and return the parsed JSON response.
        """
        if not self.available:
            raise RuntimeError("Chromatic Sanctum binary is not available.")

        cmd = [self.binary_path] + args
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Binary execution failed: {e.stderr}") from e
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Failed to parse JSON output from binary: {e}") from e

    def analyze_pixel(self, r: int, g: int, b: int, depth: str = "24-bit-rgb") -> Dict[str, Any]:
        """
        Analyze a pixel's structure and simulate its appearance at a specific bit depth.

        Args:
            r, g, b: RGB values (0-255).
            depth: Bit depth simulation ("1-bit", "8-bit-gray", "24-bit-rgb").

        Returns:
            Dictionary containing the analysis result.
        """
        args = [
            "--mode", "analyze",
            "--rgb", str(r), str(g), str(b),
            "--depth", depth
        ]
        return self._run_command(args)

    def mix_colors(self, color1: Tuple[int, int, int], color2: Tuple[int, int, int]) -> Dict[str, Any]:
        """
        Simulate additive light mixing of two colors.

        Args:
            color1: Tuple of (r, g, b).
            color2: Tuple of (r, g, b).

        Returns:
            Dictionary containing the mixing result and philosophy.
        """
        args = [
            "--mode", "mix",
            "--color1", str(color1[0]), str(color1[1]), str(color1[2]),
            "--color2", str(color2[0]), str(color2[1]), str(color2[2])
        ]
        return self._run_command(args)
