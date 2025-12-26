"""GPT-SoVITS TTS engine for high-quality voice synthesis."""

import os
import sys
import tempfile
from pathlib import Path
from typing import Optional
import numpy as np

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import GPTSOVITS_MODEL_DIR, GPTSOVITS_USE_ONNX, GPTSOVITS_QUANTIZED, AUDIO_CACHE_DIR


class GPTSoVITSTTS:
    """GPT-SoVITS text-to-speech engine."""
    
    def __init__(self, model_dir: Optional[str] = None, use_onnx: Optional[bool] = None, quantized: Optional[bool] = None):
        """
        Initialize GPT-SoVITS TTS engine.
        
        Args:
            model_dir: Directory containing model files
            use_onnx: Use ONNX models (default: from config)
            quantized: Use quantized INT8 models (default: from config)
        """
        self.model_dir = Path(model_dir) if model_dir else GPTSOVITS_MODEL_DIR
        self.use_onnx = use_onnx if use_onnx is not None else GPTSOVITS_USE_ONNX
        self.quantized = quantized if quantized is not None else GPTSOVITS_QUANTIZED
        
        self.gpt_model = None
        self.vits_model = None
        self.gpt_session = None
        self.vits_session = None
        self.device = 'cpu'
        
        self._init_models()
    
    def _init_models(self):
        """Initialize models (ONNX or PyTorch)."""
        if self.use_onnx:
            self._init_onnx_models()
        else:
            self._init_pytorch_models()
    
    def _init_onnx_models(self):
        """Initialize ONNX models."""
        try:
            import onnxruntime as ort
            
            # Determine model file names
            if self.quantized:
                gpt_file = self.model_dir / 'onnx' / 'tars_gpt_int8.onnx'
                vits_file = self.model_dir / 'onnx' / 'tars_vits_int8.onnx'
            else:
                gpt_file = self.model_dir / 'onnx' / 'tars_gpt_fp32.onnx'
                vits_file = self.model_dir / 'onnx' / 'tars_vits_fp32.onnx'
            
            # Fallback to FP32 if INT8 not found
            if self.quantized and not gpt_file.exists():
                print("WARNING: INT8 models not found, using FP32")
                gpt_file = self.model_dir / 'onnx' / 'tars_gpt_fp32.onnx'
                vits_file = self.model_dir / 'onnx' / 'tars_vits_fp32.onnx'
            
            if not gpt_file.exists() or not vits_file.exists():
                print(f"ERROR: ONNX models not found in {self.model_dir / 'onnx'}")
                print("Expected files:")
                print(f"  - {gpt_file}")
                print(f"  - {vits_file}")
                print("\nRun: python scripts/export_onnx.py --model-dir", self.model_dir)
                sys.exit(1)
            
            # Create inference sessions
            providers = ['CPUExecutionProvider']
            try:
                import onnxruntime as ort
                if ort.get_device() == 'GPU':
                    providers = ['CUDAExecutionProvider', 'CPUExecutionProvider']
            except:
                pass
            
            self.gpt_session = ort.InferenceSession(str(gpt_file), providers=providers)
            self.vits_session = ort.InferenceSession(str(vits_file), providers=providers)
            
            print(f"✓ GPT-SoVITS ONNX models loaded from {self.model_dir}")
            if self.quantized:
                print("  Using INT8 quantized models")
            else:
                print("  Using FP32 models")
            
        except ImportError:
            print("ERROR: onnxruntime not installed")
            print("Install with: pip install onnxruntime")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to load ONNX models: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def _init_pytorch_models(self):
        """Initialize PyTorch models."""
        try:
            import torch
            
            # Find model files
            s1_models = list(self.model_dir.glob('**/*s1*.pth'))
            s2_models = list(self.model_dir.glob('**/*s2*.pth'))
            
            if not s1_models:
                s1_models = list(self.model_dir.glob('**/*gpt*.pth'))
            if not s2_models:
                s2_models = list(self.model_dir.glob('**/*vits*.pth'))
            
            if not s1_models or not s2_models:
                print(f"ERROR: PyTorch models not found in {self.model_dir}")
                print("Expected .pth files for Stage 1 (GPT) and Stage 2 (VITS)")
                sys.exit(1)
            
            # Determine device
            if torch.cuda.is_available():
                self.device = 'cuda'
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                self.device = 'mps'
            else:
                self.device = 'cpu'
            
            # Load models
            # Note: Actual loading depends on GPT-SoVITS model structure
            # This is a placeholder - actual implementation would load the models
            # using GPT-SoVITS API or model loading utilities
            
            print(f"✓ GPT-SoVITS PyTorch models loaded on {self.device}")
            print("NOTE: PyTorch inference not fully implemented")
            print("Consider using ONNX models for better performance")
            
        except ImportError:
            print("ERROR: PyTorch not installed")
            print("Install with: pip install torch")
            sys.exit(1)
        except Exception as e:
            print(f"ERROR: Failed to load PyTorch models: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    def synthesize(self, text: str, output_path: Optional[str] = None, 
                   speed: float = 1.0, emotion: Optional[str] = None) -> Optional[str]:
        """
        Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            output_path: Optional path to save audio file
            speed: Speaking speed multiplier (default: 1.0)
            emotion: Optional emotion style (if supported)
            
        Returns:
            Path to generated audio file, or None if failed
        """
        if not text or not text.strip():
            return None
        
        if self.use_onnx:
            return self._synthesize_onnx(text, output_path, speed, emotion)
        else:
            return self._synthesize_pytorch(text, output_path, speed, emotion)
    
    def _synthesize_onnx(self, text: str, output_path: Optional[str], 
                         speed: float, emotion: Optional[str]) -> Optional[str]:
        """Synthesize using ONNX models."""
        try:
            # Generate output path if not provided
            if not output_path:
                AUDIO_CACHE_DIR.mkdir(exist_ok=True)
                import hashlib
                text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
                output_path = str(AUDIO_CACHE_DIR / f"gptsovits_{text_hash}.wav")
            
            # Preprocess text (phonemization, etc.)
            # This would typically use GPT-SoVITS text processing
            # For now, we'll use a simplified approach
            
            # Stage 1: GPT generates semantic tokens (prosody)
            # Note: Actual implementation requires GPT-SoVITS text processing pipeline
            # This is a placeholder that shows the structure
            
            # Stage 2: VITS synthesizes waveform from tokens
            # Note: Actual implementation requires proper token handling
            
            # For now, return a placeholder
            # In production, this would:
            # 1. Process text through GPT-SoVITS text encoder
            # 2. Run GPT model to generate semantic tokens
            # 3. Run VITS model to generate waveform
            # 4. Save audio file
            
            print("WARNING: ONNX inference not fully implemented")
            print("This requires GPT-SoVITS inference pipeline integration")
            print("For now, using PyTorch inference if available")
            
            # Fallback to PyTorch if available
            if not self.use_onnx:
                return self._synthesize_pytorch(text, output_path, speed, emotion)
            
            return None
            
        except Exception as e:
            print(f"Error synthesizing with ONNX: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _synthesize_pytorch(self, text: str, output_path: Optional[str],
                            speed: float, emotion: Optional[str]) -> Optional[str]:
        """Synthesize using PyTorch models."""
        try:
            # This would use GPT-SoVITS Python API
            # For now, this is a placeholder
            
            print("WARNING: PyTorch inference requires GPT-SoVITS API integration")
            print("Please use ONNX models or integrate GPT-SoVITS inference pipeline")
            
            return None
            
        except Exception as e:
            print(f"Error synthesizing with PyTorch: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def is_available(self) -> bool:
        """Check if TTS engine is available."""
        if self.use_onnx:
            return self.gpt_session is not None and self.vits_session is not None
        else:
            return self.gpt_model is not None and self.vits_model is not None

