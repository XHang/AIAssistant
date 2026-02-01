#!/usr/bin/env bash

set -e

echo "============================================"
echo "  HuggingFace Model -> GGUF Conversion Tool"
echo "============================================"
echo

# ---------------------------------------------------------
# Step 0 — Check sentencepiece
# ---------------------------------------------------------
echo "Checking Python package: sentencepiece ..."
python3 -c "import sentencepiece" 2>/dev/null || {
    echo "sentencepiece not found. Installing..."
    pip3 install sentencepiece || {
        echo "[ERROR] Failed to install sentencepiece."
        echo "Please install manually: pip3 install sentencepiece"
        exit 1
    }
    echo "sentencepiece installed successfully."
}
echo

# ---------------------------------------------------------
# Step 1 — Ask if llama.cpp exists
# ---------------------------------------------------------
read -p "Have you already cloned the llama.cpp repository? (y/n): " HAS_CLONE

if [[ "$HAS_CLONE" =~ ^[Yy]$ ]]; then
    read -p "Enter the absolute path to your llama.cpp directory: " LLAMA_DIR

    if [[ ! -f "$LLAMA_DIR/convert_hf_to_gguf.py" ]]; then
        echo "[ERROR] convert_hf_to_gguf.py not found in: $LLAMA_DIR"
        exit 1
    fi
else
    read -p "Enter the directory where llama.cpp should be cloned: " CLONE_DIR
    mkdir -p "$CLONE_DIR"
    cd "$CLONE_DIR"
    echo "Cloning llama.cpp..."
    git clone https://github.com/ggml-org/llama.cpp
    LLAMA_DIR="$CLONE_DIR/llama.cpp"
fi

echo
echo "llama.cpp directory: $LLAMA_DIR"
echo

# ---------------------------------------------------------
# Step 2 — Ask for model directory
# ---------------------------------------------------------
read -p "Enter the absolute path to your HuggingFace model folder: " MODEL_DIR

if [[ ! -d "$MODEL_DIR" ]]; then
    echo "[ERROR] Model directory does not exist."
    exit 1
fi

MODEL_NAME=$(basename "$MODEL_DIR")
OUTPUT_FILE="$MODEL_DIR/${MODEL_NAME}-gguf.gguf"

echo
echo "Model name: $MODEL_NAME"
echo "Output file: $OUTPUT_FILE"
echo

# ---------------------------------------------------------
# Step 3 — Run conversion
# ---------------------------------------------------------
echo "Running conversion..."
cd "$LLAMA_DIR"

python3 convert_hf_to_gguf.py "$MODEL_DIR" --outfile "$OUTPUT_FILE"
STATUS=$?

if [[ $STATUS -ne 0 ]]; then
    echo
    echo "[ERROR] Python conversion failed."
    exit 1
fi

echo
echo "============================================"
echo "Conversion completed!"
echo "GGUF file generated at:"
echo "$OUTPUT_FILE"
echo "============================================"
echo
