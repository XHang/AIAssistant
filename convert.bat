@echo off
setlocal enabledelayedexpansion

echo ============================================
echo   HuggingFace Model -> GGUF Conversion Tool
echo ============================================
echo.

:: ---------------------------------------------------------
:: Step 0 ！ Check if sentencepiece is installed
:: ---------------------------------------------------------
echo Checking Python package: sentencepiece ...
python -c "import sentencepiece" 2>nul

if errorlevel 1 (
    echo sentencepiece not found. Installing now...
    python -m pip install sentencepiece

    if errorlevel 1 (
        echo.
        echo [ERROR] Failed to install sentencepiece.
        echo Please install it manually: pip install sentencepiece
        pause
        exit /b
    )

    echo sentencepiece installed successfully.
) else (
    echo sentencepiece is already installed.
)

echo.

:: ---------------------------------------------------------
:: Step 1 ！ Ask if llama.cpp exists
:: ---------------------------------------------------------
set /p HAS_CLONE=Have you already cloned the llama.cpp repository? (y/n):

if /I "%HAS_CLONE%"=="y" (
    echo.
    set /p LLAMA_DIR=Enter the absolute path to your llama.cpp directory:
    echo Checking: "!LLAMA_DIR!\convert_hf_to_gguf.py"

    if not exist "!LLAMA_DIR!\convert_hf_to_gguf.py" (
        echo.
        echo [ERROR] convert_hf_to_gguf.py not found in the specified directory.
        pause
        exit /b
    )
) else (
    echo.
    set /p CLONE_DIR=Enter the directory where llama.cpp should be cloned:
    if not exist "%CLONE_DIR%" mkdir "%CLONE_DIR%"
    echo Cloning llama.cpp...
    cd /d "%CLONE_DIR%"
    git clone https://github.com/ggml-org/llama.cpp
    set LLAMA_DIR=%CLONE_DIR%\llama.cpp
)

echo.
echo llama.cpp directory: !LLAMA_DIR!
echo.

:: ---------------------------------------------------------
:: Step 2 ！ Ask for model directory
:: ---------------------------------------------------------
set /p MODEL_DIR=Enter the absolute path to your HuggingFace model folder:

if not exist "%MODEL_DIR%" (
    echo.
    echo [ERROR] Model directory does not exist.
    pause
    exit /b
)

for %%A in ("%MODEL_DIR%") do set MODEL_NAME=%%~nxA
set OUTPUT_FILE=%MODEL_DIR%\%MODEL_NAME%-gguf.gguf

echo.
echo Model name: %MODEL_NAME%
echo Output file: %OUTPUT_FILE%
echo.

:: ---------------------------------------------------------
:: Step 3 ！ Run conversion
:: ---------------------------------------------------------
echo Running conversion...
cd /d "!LLAMA_DIR!"
python convert_hf_to_gguf.py "%MODEL_DIR%" --outfile "%OUTPUT_FILE%"

if errorlevel 1 (
    echo.
    echo [ERROR] Python conversion failed.
    pause
    exit /b
)

echo.
echo ============================================
echo Conversion completed!
echo GGUF file generated at:
echo %OUTPUT_FILE%
echo ============================================
echo.

pause
exit /b
