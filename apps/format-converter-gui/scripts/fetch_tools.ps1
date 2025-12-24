# fetch_tools.ps1
# Downloads FFmpeg, ImageMagick, and Pandoc for Windows
# Run from the apps/format-converter-gui directory

param(
    [string]$ToolsDir = "tools"
)

$ErrorActionPreference = "Stop"

# Tool versions - update these to get newer versions
$FFmpegVersion = "latest"  # Using latest essentials build
$ImageMagickVersion = "7.1.1-21"
$PandocVersion = "3.1.11"

# Create tools directory if it doesn't exist
$FullToolsDir = Join-Path $PSScriptRoot ".." $ToolsDir
New-Item -ItemType Directory -Force -Path $FullToolsDir | Out-Null

Write-Host "Tools directory: $FullToolsDir" -ForegroundColor Cyan

# Define tool URLs
$FFmpegUrl = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$ImageMagickUrl = "https://imagemagick.org/archive/binaries/ImageMagick-${ImageMagickVersion}-portable-Q16-x64.zip"
$PandocUrl = "https://github.com/jgm/pandoc/releases/download/${PandocVersion}/pandoc-${PandocVersion}-windows-x86_64.zip"

# Download and extract FFmpeg
$FFmpegDir = Join-Path $FullToolsDir "ffmpeg"
if (-not (Test-Path (Join-Path $FFmpegDir "bin/ffmpeg.exe"))) {
    Write-Host "Downloading FFmpeg..." -ForegroundColor Yellow
    $FFmpegZip = Join-Path $env:TEMP "ffmpeg.zip"
    
    try {
        Invoke-WebRequest -Uri $FFmpegUrl -OutFile $FFmpegZip -UseBasicParsing
        Write-Host "Extracting FFmpeg..." -ForegroundColor Yellow
        
        # Extract to temp location first
        $TempExtract = Join-Path $env:TEMP "ffmpeg_extract"
        if (Test-Path $TempExtract) { Remove-Item $TempExtract -Recurse -Force }
        Expand-Archive -Path $FFmpegZip -DestinationPath $TempExtract -Force
        
        # Find the ffmpeg folder (usually ffmpeg-*-essentials_build)
        $ExtractedFolder = Get-ChildItem -Path $TempExtract -Directory | Select-Object -First 1
        
        # Move to final location
        if (Test-Path $FFmpegDir) { Remove-Item $FFmpegDir -Recurse -Force }
        Move-Item -Path $ExtractedFolder.FullName -Destination $FFmpegDir
        
        # Cleanup
        Remove-Item $FFmpegZip -Force
        Remove-Item $TempExtract -Recurse -Force
        
        Write-Host "FFmpeg installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "Error downloading FFmpeg: $_" -ForegroundColor Red
        throw
    }
}
else {
    Write-Host "FFmpeg already exists" -ForegroundColor Green
}

# Download and extract ImageMagick
$ImageMagickDir = Join-Path $FullToolsDir "imagemagick"
if (-not (Test-Path (Join-Path $ImageMagickDir "magick.exe"))) {
    Write-Host "Downloading ImageMagick..." -ForegroundColor Yellow
    $ImageMagickZip = Join-Path $env:TEMP "imagemagick.zip"
    
    try {
        Invoke-WebRequest -Uri $ImageMagickUrl -OutFile $ImageMagickZip -UseBasicParsing
        Write-Host "Extracting ImageMagick..." -ForegroundColor Yellow
        
        # Create directory and extract
        New-Item -ItemType Directory -Force -Path $ImageMagickDir | Out-Null
        Expand-Archive -Path $ImageMagickZip -DestinationPath $ImageMagickDir -Force
        
        # Cleanup
        Remove-Item $ImageMagickZip -Force
        
        Write-Host "ImageMagick installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "Error downloading ImageMagick: $_" -ForegroundColor Red
        throw
    }
}
else {
    Write-Host "ImageMagick already exists" -ForegroundColor Green
}

# Download and extract Pandoc
$PandocDir = Join-Path $FullToolsDir "pandoc"
if (-not (Test-Path (Join-Path $PandocDir "pandoc.exe"))) {
    Write-Host "Downloading Pandoc..." -ForegroundColor Yellow
    $PandocZip = Join-Path $env:TEMP "pandoc.zip"
    
    try {
        Invoke-WebRequest -Uri $PandocUrl -OutFile $PandocZip -UseBasicParsing
        Write-Host "Extracting Pandoc..." -ForegroundColor Yellow
        
        # Extract to temp location first
        $TempExtract = Join-Path $env:TEMP "pandoc_extract"
        if (Test-Path $TempExtract) { Remove-Item $TempExtract -Recurse -Force }
        Expand-Archive -Path $PandocZip -DestinationPath $TempExtract -Force
        
        # Find the pandoc folder (usually pandoc-*)
        $ExtractedFolder = Get-ChildItem -Path $TempExtract -Directory | Select-Object -First 1
        
        # Move to final location
        if (Test-Path $PandocDir) { Remove-Item $PandocDir -Recurse -Force }
        Move-Item -Path $ExtractedFolder.FullName -Destination $PandocDir
        
        # Cleanup
        Remove-Item $PandocZip -Force
        Remove-Item $TempExtract -Recurse -Force
        
        Write-Host "Pandoc installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "Error downloading Pandoc: $_" -ForegroundColor Red
        throw
    }
}
else {
    Write-Host "Pandoc already exists" -ForegroundColor Green
}

Write-Host "`nAll tools downloaded successfully!" -ForegroundColor Green
Write-Host "FFmpeg: $FFmpegDir\bin\ffmpeg.exe"
Write-Host "ImageMagick: $ImageMagickDir\magick.exe"
Write-Host "Pandoc: $PandocDir\pandoc.exe"
