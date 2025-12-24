"""Video converter using FFmpeg."""

import subprocess
from pathlib import Path
from typing import Optional, Callable

from .converter_base import BaseConverter
from .utils import get_ffmpeg_path, get_ffprobe_path, parse_ffmpeg_progress, calculate_progress


class VideoConverter(BaseConverter):
    """Converts videos using FFmpeg."""
    
    SUPPORTED_FORMATS = {
        'input': ['mp4', 'avi', 'mkv', 'mov', 'flv', 'wmv', 'webm', 'mpeg', 'mpg', 'm4v'],
        'output': ['mp4']
    }
    
    def convert(
        self,
        input_path: Path,
        output_path: Path,
        output_format: str,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> bool:
        """Convert a video using FFmpeg."""
        ffmpeg_path = get_ffmpeg_path()
        
        if not ffmpeg_path:
            self._log("Error: FFmpeg not found", log_callback)
            return False
        
        self.cancelled = False
        self._log(f"Converting {input_path.name} to {output_format}...", log_callback)
        
        # Get duration for progress calculation
        duration = self._get_duration(input_path)
        if duration:
            self._log(f"Duration: {duration:.2f} seconds", log_callback)
        
        try:
            # Build command with progress output
            cmd = [
                str(ffmpeg_path),
                '-i', str(input_path),
                '-c:v', 'libx264',  # H.264 video codec
                '-c:a', 'aac',      # AAC audio codec
                '-preset', 'medium',
                '-crf', '23',
                '-progress', 'pipe:1',
                '-nostats',
                '-y',  # Overwrite output file
                str(output_path)
            ]
            
            self._log(f"Running: {' '.join(cmd)}", log_callback)
            
            # Run conversion
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Parse progress output
            for line in iter(self.process.stdout.readline, ''):
                if self.cancelled:
                    break
                
                parsed = parse_ffmpeg_progress(line)
                if parsed and parsed[0] == 'out_time_ms':
                    try:
                        time_us = int(parsed[1])
                        progress = calculate_progress(time_us, duration)
                        if progress is not None:
                            self._progress(progress, progress_callback)
                            self._log(f"Progress: {progress*100:.1f}%", log_callback)
                    except (ValueError, TypeError):
                        pass
            
            # Wait for completion
            self.process.wait()
            
            # Read any stderr output
            stderr = self.process.stderr.read()
            
            if self.cancelled:
                self._log("Conversion cancelled", log_callback)
                return False
            
            if self.process.returncode == 0:
                self._log("Conversion completed successfully", log_callback)
                self._progress(1.0, progress_callback)
                return True
            else:
                self._log(f"Conversion failed with code {self.process.returncode}", log_callback)
                if stderr:
                    # Extract error message
                    error_lines = [l for l in stderr.split('\n') if 'error' in l.lower()]
                    if error_lines:
                        self._log(f"Error: {error_lines[-1]}", log_callback)
                return False
                
        except Exception as e:
            self._log(f"Error: {str(e)}", log_callback)
            return False
        finally:
            self.process = None
    
    def _get_duration(self, input_path: Path) -> Optional[float]:
        """Get video duration in seconds using ffprobe."""
        ffprobe_path = get_ffprobe_path()
        if not ffprobe_path:
            return None
        
        try:
            cmd = [
                str(ffprobe_path),
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                str(input_path)
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return float(result.stdout.strip())
        except Exception:
            pass
        
        return None
