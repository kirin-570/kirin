# Format Converter GUI

A Windows GUI application for converting images, videos, audio files, and documents using industry-standard tools.

## Features

- **Image Conversion**: Convert between PNG, JPG, WEBP, TIFF, BMP using ImageMagick
- **Video Conversion**: Convert various video formats to MP4 (H.264 + AAC) using FFmpeg with progress tracking
- **Audio Conversion**: Convert audio files to MP3, AAC, or WAV using FFmpeg
- **Document Conversion**: Convert between Markdown, HTML, DOCX, and optionally PDF using Pandoc
- **Real-time Progress**: Visual progress bar with percentage for video and audio conversions
- **Detailed Logging**: View conversion logs in real-time
- **Tool Status**: Check installed tools and their versions via Settings dialog

## Requirements

- Windows 10 or later
- Python 3.8 or later (for development)
- PowerShell (for downloading tools and building)

## Quick Start

### 1. Setup Development Environment

```powershell
# Navigate to the app directory
cd apps/format-converter-gui

# Create virtual environment (optional but recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -e .
```

### 2. Download Required Tools

The application requires three external tools. Run the download script to fetch them:

```powershell
.\scripts\fetch_tools.ps1
```

This will download and extract:
- **FFmpeg** (video/audio conversion) → `tools/ffmpeg/`
- **ImageMagick** (image conversion) → `tools/imagemagick/`
- **Pandoc** (document conversion) → `tools/pandoc/`

The script is idempotent and can be run multiple times safely.

### 3. Run the Application (Development)

```powershell
python -m format_converter_gui.main
```

Or using the installed script:

```powershell
format-converter-gui
```

## Building the Application

### Build Executable

```powershell
.\scripts\build.ps1
```

This creates a standalone application in `dist/FormatConverter/`.

### Prepare Distribution

After building, you need to copy the tools folder to the distribution:

```powershell
# Make sure tools are downloaded
.\scripts\fetch_tools.ps1

# Copy tools to distribution
Copy-Item -Recurse tools dist/FormatConverter/
```

The final distribution structure should be:
```
dist/FormatConverter/
├── FormatConverter.exe
├── tools/
│   ├── ffmpeg/
│   │   └── bin/
│   │       ├── ffmpeg.exe
│   │       └── ffprobe.exe
│   ├── imagemagick/
│   │   └── magick.exe
│   └── pandoc/
│       └── pandoc.exe
└── [other PyInstaller files...]
```

### Running the Built Application

```powershell
cd dist/FormatConverter
.\FormatConverter.exe
```

## Usage

### Image Conversion

1. Go to the **Image** tab
2. Click **Browse...** next to "Input File" and select an image
3. Choose the output format (PNG, JPG, WEBP)
4. Click **Browse...** next to "Output File" to set save location (or use auto-generated)
5. Click **Convert**

**Supported Input Formats**: PNG, JPG, JPEG, WEBP, TIFF, BMP, GIF  
**Supported Output Formats**: PNG, JPG, WEBP

### Video Conversion

1. Go to the **Video** tab
2. Select input video file
3. Output format is currently fixed to MP4 (H.264 + AAC)
4. Set output location
5. Click **Convert** and monitor progress

**Supported Input Formats**: MP4, AVI, MKV, MOV, FLV, WMV, WEBM, MPEG, MPG, M4V  
**Supported Output Formats**: MP4

Progress is tracked by parsing FFmpeg output, showing percentage completion in real-time.

### Audio Conversion

1. Go to the **Audio** tab
2. Select input audio file
3. Choose output format (MP3, AAC, WAV)
4. Set output location
5. Click **Convert** and monitor progress

**Supported Input Formats**: MP3, WAV, FLAC, AAC, OGG, WMA, M4A, OPUS  
**Supported Output Formats**: MP3, AAC, WAV

### Document Conversion

1. Go to the **Document** tab
2. Select input document
3. Choose output format (DOCX, HTML, MD, PDF)
4. Set output location
5. Click **Convert**

**Supported Input Formats**: MD, Markdown, HTML, DOCX, TXT, RST  
**Supported Output Formats**: DOCX, HTML, MD, PDF

**Note**: PDF conversion requires LaTeX to be installed separately. If PDF conversion fails, the log will indicate that LaTeX (MiKTeX or TeX Live) is needed.

### Settings

Access **Tools → Settings** to view:
- Tool discovery status (found/not found)
- Tool versions
- Installation paths

Use the **Refresh** button after installing tools to update the status.

## Cancelling Conversions

Click the **Cancel** button during a conversion to stop it. The process will be terminated gracefully.

## Troubleshooting

### Tools Not Found

**Problem**: Application shows "Tool not found" errors.

**Solution**:
1. Run `.\scripts\fetch_tools.ps1` to download tools
2. Ensure `tools/` folder is next to the `.exe` (for built app)
3. Check Settings dialog to verify tool paths

### PDF Conversion Fails

**Problem**: Document to PDF conversion fails.

**Solution**: PDF conversion requires LaTeX. Install one of:
- [MiKTeX](https://miktex.org/download) (recommended for Windows)
- [TeX Live](https://www.tug.org/texlive/)

### Video Conversion Progress Not Showing

**Problem**: Progress bar doesn't update during video conversion.

**Solution**: This is expected for very short videos. For longer videos, progress updates every few seconds.

### ImageMagick Errors

**Problem**: Image conversion fails with policy errors.

**Solution**: The portable ImageMagick version is configured to avoid policy restrictions. If issues persist, check the log for specific errors.

## Project Structure

```
apps/format-converter-gui/
├── src/
│   └── format_converter_gui/
│       ├── __init__.py
│       ├── main.py                    # Entry point
│       ├── main_window.py              # Main window
│       ├── converter_tab.py            # Tab widget for conversions
│       ├── settings_dialog.py          # Settings dialog
│       ├── utils.py                    # Path utilities
│       ├── converter_base.py           # Base converter class
│       ├── converter_image.py          # Image converter
│       ├── converter_video.py          # Video converter
│       ├── converter_audio.py          # Audio converter
│       └── converter_document.py       # Document converter
├── scripts/
│   ├── fetch_tools.ps1                 # Download tools script
│   └── build.ps1                       # Build script
├── format_converter.spec               # PyInstaller spec
├── pyproject.toml                      # Project configuration
├── .gitignore
└── README.md
```

## Development

### Running Tests

Currently, this is a GUI application without automated tests. Manual testing is recommended:

1. Test each converter type with various input formats
2. Verify progress reporting
3. Test cancellation
4. Check tool detection in Settings

### Adding New Formats

To add support for new formats:

1. Update the `SUPPORTED_FORMATS` dict in the relevant converter class
2. Add format-specific conversion logic if needed
3. Update this README

### Code Style

- Follow PEP 8 guidelines
- Use type hints where applicable
- Document classes and complex methods

## Technical Details

### Tool Integration

- **FFmpeg**: Uses `-progress pipe:1 -nostats` for real-time progress parsing
- **ImageMagick**: Sets `MAGICK_HOME` environment variable and prepends to PATH
- **Pandoc**: Called with `--standalone` flag for complete document output

### Path Resolution

The app resolves tool paths relative to the executable directory:
- When frozen (built): `sys.executable` parent directory
- When running as script: Project root directory

This ensures tools are found in both development and distribution modes.

### Threading

Conversions run in separate QThread workers to prevent UI freezing. Progress and log updates are signaled back to the main thread for safe GUI updates.

## License

This application is a GUI wrapper around open-source tools:
- FFmpeg: LGPL/GPL (depending on build)
- ImageMagick: Apache 2.0
- Pandoc: GPL

## Support

For issues or questions, please open an issue in the repository.
