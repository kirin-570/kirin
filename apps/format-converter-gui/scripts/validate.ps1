# validate.ps1
# Quick validation script to check the installation

$ErrorActionPreference = "Stop"

Write-Host "`n=== Format Converter GUI Validation ===" -ForegroundColor Cyan

# Check Python
Write-Host "`n1. Checking Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   ✓ $pythonVersion" -ForegroundColor Green
}
catch {
    Write-Host "   ✗ Python not found" -ForegroundColor Red
    exit 1
}

# Check project structure
Write-Host "`n2. Checking project structure..." -ForegroundColor Yellow
$requiredFiles = @(
    "pyproject.toml",
    "format_converter.spec",
    "README.md",
    "scripts/fetch_tools.ps1",
    "scripts/build.ps1",
    "src/format_converter_gui/__init__.py",
    "src/format_converter_gui/main.py"
)

foreach ($file in $requiredFiles) {
    if (Test-Path $file) {
        Write-Host "   ✓ $file" -ForegroundColor Green
    }
    else {
        Write-Host "   ✗ $file missing" -ForegroundColor Red
    }
}

# Check if virtual environment should be created
Write-Host "`n3. Checking Python packages..." -ForegroundColor Yellow
$hasVenv = Test-Path "venv"
if (-not $hasVenv) {
    Write-Host "   ! Virtual environment not found" -ForegroundColor Yellow
    Write-Host "   Suggestion: python -m venv venv" -ForegroundColor Gray
}

# Try to import the package
try {
    python -c "import sys; sys.path.insert(0, 'src'); from format_converter_gui import __version__; print(f'   ✓ Package version: {__version__}')" 2>&1
    if ($LASTEXITCODE -eq 0) {
        # Success message already printed by Python
    }
}
catch {
    Write-Host "   ✗ Package import failed" -ForegroundColor Red
    Write-Host "   Suggestion: pip install -e ." -ForegroundColor Gray
}

# Check tools
Write-Host "`n4. Checking conversion tools..." -ForegroundColor Yellow
$tools = @{
    "FFmpeg"      = "tools/ffmpeg/bin/ffmpeg.exe"
    "FFprobe"     = "tools/ffmpeg/bin/ffprobe.exe"
    "ImageMagick" = "tools/imagemagick/magick.exe"
    "Pandoc"      = "tools/pandoc/pandoc.exe"
}

$allToolsFound = $true
foreach ($tool in $tools.GetEnumerator()) {
    if (Test-Path $tool.Value) {
        Write-Host "   ✓ $($tool.Key) found at $($tool.Value)" -ForegroundColor Green
    }
    else {
        Write-Host "   ✗ $($tool.Key) not found" -ForegroundColor Red
        $allToolsFound = $false
    }
}

if (-not $allToolsFound) {
    Write-Host "   Suggestion: .\scripts\fetch_tools.ps1" -ForegroundColor Gray
}

# Check if built
Write-Host "`n5. Checking build..." -ForegroundColor Yellow
if (Test-Path "dist/FormatConverter/FormatConverter.exe") {
    Write-Host "   ✓ Built executable found" -ForegroundColor Green
    
    # Check if tools are in dist
    $distTools = Test-Path "dist/FormatConverter/tools"
    if ($distTools) {
        Write-Host "   ✓ Tools folder in distribution" -ForegroundColor Green
    }
    else {
        Write-Host "   ✗ Tools folder missing from distribution" -ForegroundColor Red
        Write-Host "   Suggestion: Copy-Item -Recurse tools dist/FormatConverter/" -ForegroundColor Gray
    }
}
else {
    Write-Host "   - Not built yet" -ForegroundColor Gray
    Write-Host "   Suggestion: .\scripts\build.ps1" -ForegroundColor Gray
}

Write-Host "`n=== Validation Complete ===" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Install dependencies: pip install -e ." -ForegroundColor White
Write-Host "  2. Download tools: .\scripts\fetch_tools.ps1" -ForegroundColor White
Write-Host "  3. Run in dev mode: python -m format_converter_gui.main" -ForegroundColor White
Write-Host "  4. Or build: .\scripts\build.ps1" -ForegroundColor White
Write-Host ""
