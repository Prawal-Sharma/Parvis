#!/bin/bash
# Download language models for Pi-Jarvis
# Phase 3: Language Model Models

set -e  # Exit on any error

echo "🧠 Pi-Jarvis Phase 3: Downloading Language Models"
echo "================================================="

# Detect which LLM backend is installed
if [ -d "models/llama.cpp" ]; then
    BACKEND="llama.cpp"
    echo "📋 Detected backend: llama.cpp"
elif command -v ollama &> /dev/null; then
    BACKEND="ollama"
    echo "📋 Detected backend: Ollama"
else
    echo "❌ No LLM backend found. Run ./setup/install_llm.sh first"
    exit 1
fi

echo ""
echo "Choose a language model for your Pi 4:"
echo "1. TinyLlama 1.1B (faster, good for Pi 4)"
echo "2. Phi-3-mini 3.8B (slower, better quality)" 
echo "3. Both models"
echo ""
read -p "Enter your choice (1, 2, or 3): " model_choice

download_for_llamacpp() {
    local model_name=$1
    local model_url=$2
    local model_file=$3
    
    echo "📥 Downloading $model_name for llama.cpp..."
    
    if [ ! -f "models/$model_file" ]; then
        echo "Downloading from Hugging Face..."
        wget -O "models/$model_file" "$model_url"
        echo "✅ $model_name downloaded"
    else
        echo "ℹ️  $model_name already exists"
    fi
}

download_for_ollama() {
    local model_name=$1
    
    echo "📥 Downloading $model_name for Ollama..."
    
    # Pull model with Ollama
    if ! ollama list | grep -q "$model_name"; then
        ollama pull "$model_name"
        echo "✅ $model_name downloaded"
    else
        echo "ℹ️  $model_name already exists"
    fi
}

# Download based on choice and backend
case $model_choice in
    1|3)
        echo "📦 TinyLlama 1.1B Chat (Q4_K_M quantized)"
        if [ "$BACKEND" = "llama.cpp" ]; then
            download_for_llamacpp "TinyLlama 1.1B" \
                "https://huggingface.co/TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF/resolve/main/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf" \
                "tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf"
        else
            download_for_ollama "tinyllama"
        fi
        
        [[ $model_choice == "1" ]] && echo "🎯 TinyLlama download complete!" && exit 0
        ;;
esac

case $model_choice in
    2|3)
        echo "📦 Phi-3-mini 3.8B Instruct (Q4_K_M quantized)"
        if [ "$BACKEND" = "llama.cpp" ]; then
            download_for_llamacpp "Phi-3-mini 3.8B" \
                "https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf" \
                "Phi-3-mini-4k-instruct-q4.gguf"
        else
            download_for_ollama "phi3:mini"
        fi
        
        [[ $model_choice == "2" ]] && echo "🎯 Phi-3-mini download complete!" && exit 0
        ;;
esac

[[ $model_choice == "3" ]] && echo "🎯 Both models download complete!"

echo ""
echo "📋 Downloaded models:"
if [ "$BACKEND" = "llama.cpp" ]; then
    ls -lh models/*.gguf 2>/dev/null || echo "No GGUF models found"
else
    ollama list
fi

echo ""
echo "🚀 Next: Test language model inference"
echo "Run: python -m assistant.test_llm"