"""Lightweight FastAPI server for GPT-SoVITS inference on Raspberry Pi."""

import argparse
import os
import sys
from pathlib import Path
from typing import Optional
import tempfile

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import FileResponse
    from pydantic import BaseModel
    import uvicorn
except ImportError:
    print("ERROR: FastAPI not installed")
    print("Install with: pip install fastapi uvicorn")
    sys.exit(1)

# Add project root to path if running from project
try:
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    from core.gptsovits_tts import GPTSoVITSTTS
except ImportError:
    # Running standalone on Pi
    GPTSoVITSTTS = None


app = FastAPI(title="GPT-SoVITS Inference Server")


class TTSRequest(BaseModel):
    text: str
    speed: float = 1.0
    emotion: Optional[str] = None


# Global TTS engine (loaded at startup)
tts_engine = None


@app.on_event("startup")
async def startup_event():
    """Load models at server startup."""
    global tts_engine
    
    print("Loading GPT-SoVITS models...")
    try:
        if GPTSoVITSTTS:
            tts_engine = GPTSoVITSTTS(quantized=True, use_onnx=True)
        else:
            # Standalone mode - load models directly
            import onnxruntime as ort
            model_dir = Path(os.getenv('MODEL_DIR', './models'))
            onnx_dir = model_dir / 'onnx'
            
            gpt_model = onnx_dir / 'tars_gpt_int8.onnx'
            vits_model = onnx_dir / 'tars_vits_int8.onnx'
            
            if not gpt_model.exists() or not vits_model.exists():
                raise FileNotFoundError(f"Models not found: {onnx_dir}")
            
            # Create minimal TTS engine
            tts_engine = {
                'gpt_session': ort.InferenceSession(str(gpt_model)),
                'vits_session': ort.InferenceSession(str(vits_model)),
                'model_dir': model_dir
            }
        
        print("✓ Models loaded successfully")
    except Exception as e:
        print(f"ERROR: Failed to load models: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "running",
        "models_loaded": tts_engine is not None
    }


@app.post("/synthesize")
async def synthesize(request: TTSRequest):
    """
    Synthesize speech from text.
    
    Returns WAV audio file.
    """
    if not tts_engine:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text is required")
    
    try:
        # Generate audio
        if isinstance(tts_engine, dict):
            # Standalone mode - use ONNX directly
            audio_path = synthesize_standalone(tts_engine, request.text, request.speed)
        else:
            # Full GPTSoVITSTTS instance
            audio_path = tts_engine.synthesize(
                request.text,
                speed=request.speed,
                emotion=request.emotion
            )
        
        if not audio_path or not os.path.exists(audio_path):
            raise HTTPException(status_code=500, detail="Failed to generate audio")
        
        return FileResponse(
            audio_path,
            media_type="audio/wav",
            filename="synthesized.wav"
        )
    
    except Exception as e:
        print(f"Error synthesizing: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def synthesize_standalone(engine_dict, text, speed):
    """Synthesize using standalone ONNX models."""
    # This is a placeholder - actual implementation requires
    # GPT-SoVITS inference pipeline integration
    # For now, return None to indicate not implemented
    
    print("WARNING: Standalone ONNX inference not fully implemented")
    print("Please use full GPTSoVITSTTS class or implement inference pipeline")
    
    # Create temporary output file
    output_file = tempfile.mktemp(suffix='.wav')
    
    # TODO: Implement actual inference
    # 1. Process text (phonemization, etc.)
    # 2. Run GPT model to get semantic tokens
    # 3. Run VITS model to generate waveform
    # 4. Save to output_file
    
    return None  # Not implemented yet


def main():
    parser = argparse.ArgumentParser(description='GPT-SoVITS Inference Server for Raspberry Pi')
    parser.add_argument('--model-dir', type=str, default='./models',
                       help='Directory containing ONNX models')
    parser.add_argument('--port', type=int, default=8000,
                       help='Server port (default: 8000)')
    parser.add_argument('--host', type=str, default='0.0.0.0',
                       help='Server host (default: 0.0.0.0)')
    
    args = parser.parse_args()
    
    # Set environment variable for model directory
    os.environ['MODEL_DIR'] = args.model_dir
    
    print("=" * 60)
    print("GPT-SoVITS Inference Server")
    print("=" * 60)
    print(f"Model directory: {args.model_dir}")
    print(f"Server: http://{args.host}:{args.port}")
    print("\nStarting server...")
    
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()

