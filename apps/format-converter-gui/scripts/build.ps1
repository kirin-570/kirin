# build.ps1
# Builds the Format Converter GUI using PyInstaller
# Run from the apps/format-converter-gui directory

param(
    [switch]$Clean = $false
)

$ErrorActionPreference = "Stop"

$AppDir = Split-Path -Parent $PSScriptRoot
$SrcDir = Join-Path $AppDir "src"
$DistDir = Join-Path $AppDir "dist"
$BuildDir = Join-Path $AppDir "build"

Write-Host "Building Format Converter GUI..." -ForegroundColor Cyan

# Clean previous builds if requested
if ($Clean) {
    Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
    if (Test-Path $DistDir) { Remove-Item $DistDir -Recurse -Force }
    if (Test-Path $BuildDir) { Remove-Item $BuildDir -Recurse -Force }
}

# Check if PyInstaller is installed
try {
    pyinstaller --version | Out-Null
}
catch {
    Write-Host "PyInstaller not found. Installing..." -ForegroundColor Yellow
    pip install pyinstaller
}

# Build with PyInstaller
Write-Host "Running PyInstaller..." -ForegroundColor Yellow

$MainScript = Join-Path $SrcDir "format_converter_gui/main.py"
$SpecFile = Join-Path $AppDir "format_converter.spec"

if (Test-Path $SpecFile) {
    # Use existing spec file
    pyinstaller $SpecFile --clean
}
else {
    # Create build with command line options
    pyinstaller --name "FormatConverter" `
        --onedir `
        --windowed `
        --noconfirm `
        --clean `
        --distpath $DistDir `
        --workpath $BuildDir `
        $MainScript
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nBuild completed successfully!" -ForegroundColor Green
    Write-Host "Output directory: $DistDir\FormatConverter" -ForegroundColor Cyan
    Write-Host "`nNext steps:" -ForegroundColor Yellow
    Write-Host "1. Run '.\scripts\fetch_tools.ps1' to download required tools"
    Write-Host "2. Copy the 'tools' folder to '$DistDir\FormatConverter\'"
    Write-Host "3. Run '$DistDir\FormatConverter\FormatConverter.exe'"
}
else {
    Write-Host "`nBuild failed!" -ForegroundColor Red
    exit 1
}
