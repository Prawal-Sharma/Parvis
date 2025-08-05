#!/bin/bash
# Install Language Model backend (llama.cpp or Ollama)
# Phase 3: Language Model Integration

set -e  # Exit on any error

echo "🧠 Pi-Jarvis Phase 3: Language Model Setup"
echo "=========================================="

echo "Choose your Language Model backend:"
echo "1. llama.cpp (lightweight, C++, direct control)"
echo "2. Ollama (user-friendly, automatic management)"
echo ""
read -p "Enter your choice (1 or 2): " choice

case $choice in
    1)
        echo "📦 Installing llama.cpp..."
        
        # Clone llama.cpp if not exists
        if [ ! -d "models/llama.cpp" ]; then
            cd models
            git clone https://github.com/ggerganov/llama.cpp.git
            cd llama.cpp
        else
            echo "ℹ️  llama.cpp already cloned"
            cd models/llama.cpp
            git pull origin master
        fi
        
        # Clean previous builds
        make clean || true
        rm -rf build || true
        
        # Build with Pi 4 optimizations
        echo "🔧 Building llama.cpp with ARM optimizations..."
        mkdir -p build
        cd build
        cmake .. -DGGML_OPENBLAS=ON -DCMAKE_BUILD_TYPE=Release
        make -j4
        
        # Verify build
        if [ -f "./bin/llama-cli" ] || [ -f "./llama-cli" ]; then
            echo "✅ llama.cpp built successfully!"
        else
            echo "❌ llama.cpp build failed"
            exit 1
        fi
        
        cd ../../..
        echo "✅ llama.cpp installation complete"
        ;;
        
    2)
        echo "📦 Installing Ollama..."
        
        # Install Ollama
        curl -fsSL https://ollama.ai/install.sh | sh
        
        # Start Ollama service
        echo "🚀 Starting Ollama service..."
        sudo systemctl enable ollama || true
        sudo systemctl start ollama || true
        
        # Wait for service to start
        sleep 5
        
        # Verify installation
        if command -v ollama &> /dev/null; then
            echo "✅ Ollama installed successfully!"
            ollama --version
        else
            echo "❌ Ollama installation failed"
            exit 1
        fi
        ;;
        
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
echo "🎯 Next: Download language models"
echo "Run: ./setup/download_llm_models.sh"