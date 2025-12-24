"""Base converter class."""

import subprocess
from pathlib import Path
from typing import Optional, Callable
from abc import ABC, abstractmethod


class BaseConverter(ABC):
    """Base class for all converters."""
    
    def __init__(self):
        self.process: Optional[subprocess.Popen] = None
        self.cancelled = False
    
    @abstractmethod
    def convert(
        self,
        input_path: Path,
        output_path: Path,
        output_format: str,
        log_callback: Optional[Callable[[str], None]] = None,
        progress_callback: Optional[Callable[[float], None]] = None
    ) -> bool:
        """
        Convert a file from input to output format.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file
            output_format: Desired output format
            log_callback: Function to call with log messages
            progress_callback: Function to call with progress (0.0-1.0)
        
        Returns:
            True if conversion succeeded, False otherwise
        """
        pass
    
    def cancel(self):
        """Cancel the current conversion."""
        self.cancelled = True
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
    
    def _log(self, message: str, callback: Optional[Callable[[str], None]]):
        """Helper to log messages."""
        if callback:
            callback(message)
    
    def _progress(self, value: float, callback: Optional[Callable[[float], None]]):
        """Helper to report progress."""
        if callback:
            callback(max(0.0, min(1.0, value)))
