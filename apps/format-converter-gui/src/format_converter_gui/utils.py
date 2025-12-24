"""Tool path utilities and version detection."""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Dict, Tuple


def get_app_dir() -> Path:
    """Get the application directory (where the exe is located)."""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        return Path(sys.executable).parent
    else:
        # Running as script - use project root
        return Path(__file__).parent.parent.parent


def get_tools_dir() -> Path:
    """Get the tools directory."""
    return get_app_dir() / "tools"


def get_ffmpeg_path() -> Optional[Path]:
    """Get path to ffmpeg.exe."""
    ffmpeg_path = get_tools_dir() / "ffmpeg" / "bin" / "ffmpeg.exe"
    return ffmpeg_path if ffmpeg_path.exists() else None


def get_ffprobe_path() -> Optional[Path]:
    """Get path to ffprobe.exe."""
    ffprobe_path = get_tools_dir() / "ffmpeg" / "bin" / "ffprobe.exe"
    return ffprobe_path if ffprobe_path.exists() else None


def get_imagemagick_path() -> Optional[Path]:
    """Get path to magick.exe."""
    magick_path = get_tools_dir() / "imagemagick" / "magick.exe"
    return magick_path if magick_path.exists() else None


def get_pandoc_path() -> Optional[Path]:
    """Get path to pandoc.exe."""
    pandoc_path = get_tools_dir() / "pandoc" / "pandoc.exe"
    return pandoc_path if pandoc_path.exists() else None


def get_imagemagick_env() -> Dict[str, str]:
    """Get environment variables for ImageMagick."""
    env = os.environ.copy()
    magick_dir = get_tools_dir() / "imagemagick"
    if magick_dir.exists():
        env['MAGICK_HOME'] = str(magick_dir)
        # Prepend to PATH
        env['PATH'] = f"{magick_dir};{env.get('PATH', '')}"
    return env


def get_tool_version(tool_path: Optional[Path], version_arg: str = "--version") -> Optional[str]:
    """Get version string from a tool."""
    if not tool_path or not tool_path.exists():
        return None
    
    try:
        result = subprocess.run(
            [str(tool_path), version_arg],
            capture_output=True,
            text=True,
            timeout=5
        )
        # Return first line of output
        output = result.stdout.strip() or result.stderr.strip()
        return output.split('\n')[0] if output else None
    except Exception:
        return None


def check_tools_status() -> Dict[str, Dict[str, Optional[str]]]:
    """Check status of all tools."""
    tools = {
        "FFmpeg": {
            "path": get_ffmpeg_path(),
            "version": None,
        },
        "FFprobe": {
            "path": get_ffprobe_path(),
            "version": None,
        },
        "ImageMagick": {
            "path": get_imagemagick_path(),
            "version": None,
        },
        "Pandoc": {
            "path": get_pandoc_path(),
            "version": None,
        },
    }
    
    # Get versions
    tools["FFmpeg"]["version"] = get_tool_version(tools["FFmpeg"]["path"], "-version")
    tools["FFprobe"]["version"] = get_tool_version(tools["FFprobe"]["path"], "-version")
    tools["ImageMagick"]["version"] = get_tool_version(tools["ImageMagick"]["path"], "-version")
    tools["Pandoc"]["version"] = get_tool_version(tools["Pandoc"]["path"], "--version")
    
    return tools


def parse_ffmpeg_progress(line: str) -> Optional[Tuple[str, str]]:
    """
    Parse FFmpeg progress output line.
    
    Returns tuple of (key, value) if line is a progress line, None otherwise.
    The key 'out_time_ms' contains time in microseconds despite the name.
    """
    line = line.strip()
    if '=' in line:
        key, _, value = line.partition('=')
        return (key, value)
    return None


def calculate_progress(out_time_us: int, duration: Optional[float]) -> Optional[float]:
    """
    Calculate conversion progress from FFmpeg out_time_ms value.
    
    Args:
        out_time_us: Time in microseconds (from out_time_ms field)
        duration: Total duration in seconds (from ffprobe)
    
    Returns:
        Progress value between 0.0 and 1.0, or None if duration is invalid
    """
    if duration is None or duration <= 0:
        return None
    
    current_time = out_time_us / 1_000_000  # Convert microseconds to seconds
    return current_time / duration
