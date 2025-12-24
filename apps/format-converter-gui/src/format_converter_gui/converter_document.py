"""Document converter using Pandoc."""

import subprocess
from pathlib import Path
from typing import Optional, Callable

from .converter_base import BaseConverter
from .utils import get_pandoc_path


class DocumentConverter(BaseConverter):
    """Converts documents using Pandoc."""
    
    SUPPORTED_FORMATS = {
        'input': ['md', 'markdown', 'html', 'docx', 'txt', 'rst'],
        'output': ['docx', 'html', 'md', 'pdf']
    }
    
    def convert(
        self,
        input_path: Path,
        output_path: Path,
        output_format: str,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> bool:
        """Convert a document using Pandoc."""
        pandoc_path = get_pandoc_path()
        
        if not pandoc_path:
            self._log("Error: Pandoc not found", log_callback)
            return False
        
        self.cancelled = False
        self._log(f"Converting {input_path.name} to {output_format}...", log_callback)
        self._progress(0.1, progress_callback)
        
        # Check if PDF conversion is requested
        if output_format == 'pdf':
            self._log("Note: PDF conversion requires LaTeX to be installed separately", log_callback)
            self._log("If conversion fails, LaTeX may not be available", log_callback)
        
        try:
            # Build command
            cmd = [
                str(pandoc_path),
                str(input_path),
                '-o', str(output_path),
                '--standalone'
            ]
            
            # Add format-specific options
            if output_format == 'html':
                cmd.append('--self-contained')
            
            self._log(f"Running: {' '.join(cmd)}", log_callback)
            
            # Run conversion
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
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
                    if output_format == 'pdf' and 'pdflatex' in stderr.lower():
                        self._log("PDF conversion requires LaTeX. Please install MiKTeX or TeX Live.", log_callback)
                return False
                
        except Exception as e:
            self._log(f"Error: {str(e)}", log_callback)
            return False
        finally:
            self.process = None
