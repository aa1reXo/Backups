#!/bin/bash

# Tesseract OCR Installation Script
# Supports macOS, Ubuntu/Debian, and Windows (WSL)

echo "🔍 Installing Tesseract OCR for Multimodal PDF Processing"
echo "=================================================="

# Detect operating system
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    echo "🍎 Detected macOS"
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Installing Homebrew first..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
    
    echo "📦 Installing Tesseract OCR..."
    brew install tesseract
    
    echo "🌍 Installing additional language packs..."
    brew install tesseract-lang
    
    echo "✅ Tesseract installed successfully on macOS"
    echo "📋 Available languages:"
    tesseract --list-langs
    
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux (Ubuntu/Debian)
    echo "🐧 Detected Linux"
    
    # Check if apt is available
    if command -v apt &> /dev/null; then
        echo "📦 Installing Tesseract OCR..."
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr
        
        echo "🌍 Installing additional language packs..."
        sudo apt-get install -y \
            tesseract-ocr-eng \
            tesseract-ocr-fra \
            tesseract-ocr-spa \
            tesseract-ocr-deu \
            tesseract-ocr-ita \
            tesseract-ocr-por \
            tesseract-ocr-rus \
            tesseract-ocr-chi-sim \
            tesseract-ocr-jpn \
            tesseract-ocr-kor
        
        echo "✅ Tesseract installed successfully on Linux"
        echo "📋 Available languages:"
        tesseract --list-langs
        
    else
        echo "❌ Unsupported Linux distribution. Please install Tesseract manually."
        echo "📖 Visit: https://github.com/tesseract-ocr/tesseract"
        exit 1
    fi
    
else
    echo "❌ Unsupported operating system: $OSTYPE"
    echo "📖 Please install Tesseract manually:"
    echo "   - macOS: brew install tesseract"
    echo "   - Ubuntu/Debian: sudo apt-get install tesseract-ocr"
    echo "   - Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki"
    exit 1
fi

# Verify installation
echo ""
echo "🔍 Verifying Tesseract installation..."
if command -v tesseract &> /dev/null; then
    version=$(tesseract --version | head -n 1)
    echo "✅ Tesseract installed successfully: $version"
    
    # Test OCR
    echo "🧪 Testing OCR functionality..."
    echo "This is a test" > test_ocr.txt
    if tesseract test_ocr.txt stdout &> /dev/null; then
        echo "✅ OCR test passed"
    else
        echo "⚠️  OCR test failed - check installation"
    fi
    rm -f test_ocr.txt
    
else
    echo "❌ Tesseract installation failed"
    exit 1
fi

echo ""
echo "🎉 Tesseract OCR installation completed!"
echo "📋 Next steps:"
echo "   1. Install Python dependencies: pip install -r requirements.txt"
echo "   2. Test the multimodal processor: python test_multimodal_processor.py"
echo "   3. Start the API server: python main.py"
echo ""
echo "🔗 For more information:"
echo "   - Tesseract: https://github.com/tesseract-ocr/tesseract"
echo "   - Language packs: https://github.com/tesseract-ocr/tessdata" 