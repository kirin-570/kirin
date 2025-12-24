"""Image converter using ImageMagick."""

import subprocess
from pathlib import Path
from typing import Optional, Callable

from .converter_base import BaseConverter
from .utils import get_imagemagick_path, get_imagemagick_env


class ImageConverter(BaseConverter):
    """Converts images using ImageMagick."""
    
    SUPPORTED_FORMATS = {
        'input': ['png', 'jpg', 'jpeg', 'webp', 'tiff', 'tif', 'bmp', 'gif'],
        'output': ['png', 'jpg', 'jpeg', 'webp']
    }
    
    def convert(
        self,
        input_path: Path,
        output_path: Path,
        output_format: str,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> bool:
        """Convert an image using ImageMagick."""
        magick_path = get_imagemagick_path()
        
        if not magick_path:
            self._log("Error: ImageMagick not found", log_callback)
            return False
        
        self.cancelled = False
        self._log(f"Converting {input_path.name} to {output_format}...", log_callback)
        self._progress(0.1, progress_callback)
        
        try:
            # Build command
            cmd = [
                str(magick_path),
                str(input_path),
                str(output_path)
            ]
            
            self._log(f"Running: {' '.join(cmd)}", log_callback)
            
            # Run conversion
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=get_imagemagick_env()
            )
            
            self._progress(0.5, progress_callback)
            
            # Wait for completion
            stdout, stderr = self.process.communicate()
            
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
                    self._log(f"Error: {stderr}", log_callback)
                return False
                
        except Exception as e:
            self._log(f"Error: {str(e)}", log_callback)
            return False
        finally:
            self.process = None
