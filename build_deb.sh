#!/bin/bash
set -e

VERSION="0.1.0"
PKG_NAME="aloud"
ARCH="amd64"
DIR="${PKG_NAME}_${VERSION}-1_${ARCH}"

echo "🔨 Building standalone binary with PyInstaller..."
source .venv/bin/activate
pyinstaller main.py --name aloud --onefile --windowed --clean \
    --hidden-import=customtkinter \
    --hidden-import=PIL._tkinter_finder \
    --add-data ".venv/lib/python3.13/site-packages/piper/espeak-ng-data:piper/espeak-ng-data" \
    --add-data ".venv/lib/python3.13/site-packages/piper/tashkeel:piper/tashkeel"
deactivate

echo "📁 Creating Debian package structure in ./$DIR"
rm -rf "$DIR"
mkdir -p "$DIR/DEBIAN"
mkdir -p "$DIR/usr/bin"
mkdir -p "$DIR/usr/share/applications"
mkdir -p "$DIR/usr/share/icons/hicolor/512x512/apps"

echo "📄 Generating control file..."
cat <<EOF > "$DIR/DEBIAN/control"
Package: aloud
Version: ${VERSION}-1
Section: utils
Priority: optional
Architecture: amd64
Depends: tesseract-ocr, espeak-ng, libc6 (>= 2.31)
Maintainer: Aloud Developer <developer@example.com>
Description: Aloud PDF Reader
 A modern Linux desktop application that reads PDF files aloud using neural TTS.
 It downloads the heavy ONNX voice models on the first run to keep the install small.
EOF

echo "📄 Generating desktop entry..."
cat <<EOF > "$DIR/usr/share/applications/aloud.desktop"
[Desktop Entry]
Version=1.0
Name=Aloud
Comment=Neural TTS PDF Reader
Exec=/usr/bin/aloud
Icon=aloud
Terminal=false
Type=Application
Categories=Office;Viewer;Accessibility;
EOF

echo "📥 Copying built binary and assets..."
cp dist/aloud "$DIR/usr/bin/aloud"
chmod +x "$DIR/usr/bin/aloud"

# Use the specific user-requested theme image as the icon
cp aloud_app_theme.png "$DIR/usr/share/icons/hicolor/512x512/apps/aloud.png"

echo "📦 Building the final .deb package..."
dpkg-deb --build "$DIR"

echo "✅ Success! Built package: ${DIR}.deb"
