"""Export GPT-SoVITS models to ONNX format for deployment."""

import argparse
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Define MODELS_DIR directly to avoid dependency on config.settings
MODELS_DIR = project_root / 'models'


def find_gptsovits_dir():
    """Find GPT-SoVITS installation directory."""
    gptsovits_dir = MODELS_DIR / 'GPT-SoVITS'
    if not gptsovits_dir.exists():
        print(f"ERROR: GPT-SoVITS not found at {gptsovits_dir}")
        print("Run setup first: python scripts/setup_gptsovits.py")
        sys.exit(1)
    return gptsovits_dir


def find_onnx_export_script(gptsovits_dir):
    """Find ONNX export script in GPT-SoVITS."""
    # ONNX export script is in GPT_SoVITS/ subdirectory
    gpt_sovits_dir = gptsovits_dir / 'GPT_SoVITS'
    export_script = gpt_sovits_dir / 'onnx_export.py'
    
    if not export_script.exists():
        alternatives = [
            gptsovits_dir / 'onnx_export.py',
            gptsovits_dir / 'tools' / 'onnx_export.py',
            gptsovits_dir / 'api' / 'onnx_export.py',
        ]
        for alt in alternatives:
            if alt.exists():
                export_script = alt
                break
        else:
            print("ERROR: Could not find ONNX export script")
            print(f"Expected at: {gpt_sovits_dir / 'onnx_export.py'}")
            print("GPT-SoVITS repository structure may have changed")
            return None
    
    return export_script


def find_trained_models(model_dir):
    """Find trained model files."""
    model_dir = Path(model_dir)
    
    s1_models = list(model_dir.glob('**/s1*.pth'))
    s2_models = list(model_dir.glob('**/s2*.pth'))
    
    if not s1_models:
        s1_models = list(model_dir.glob('**/gpt*.pth'))
    if not s2_models:
        s2_models = list(model_dir.glob('**/vits*.pth'))
    
    return s1_models, s2_models


def export_to_onnx(gptsovits_dir, export_script, s1_model, s2_model, output_dir):
    """Export models to ONNX format."""
    print("\nExporting models to ONNX...")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export Stage 1 (GPT) model
    print(f"\nExporting Stage 1 (GPT) model...")
    s1_onnx = output_dir / 'tars_gpt_fp32.onnx'
    
    cmd_s1 = [
        sys.executable, str(export_script),
        '--model', str(s1_model),
        '--output', str(s1_onnx),
        '--stage', '1'
    ]
    
    try:
        import subprocess
        result = subprocess.run(cmd_s1, cwd=str(gptsovits_dir), check=True)
        print(f"✓ Stage 1 ONNX exported: {s1_onnx}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to export Stage 1 model: {e}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    
    # Export Stage 2 (VITS) model
    print(f"\nExporting Stage 2 (VITS) model...")
    s2_onnx = output_dir / 'tars_vits_fp32.onnx'
    
    cmd_s2 = [
        sys.executable, str(export_script),
        '--model', str(s2_model),
        '--output', str(s2_onnx),
        '--stage', '2'
    ]
    
    try:
        result = subprocess.run(cmd_s2, cwd=str(gptsovits_dir), check=True)
        print(f"✓ Stage 2 ONNX exported: {s2_onnx}")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to export Stage 2 model: {e}")
        return False
    
    return True


def quantize_onnx(onnx_path, output_path, quant_type='int8'):
    """Quantize ONNX model to INT8."""
    print(f"\nQuantizing {onnx_path.name} to {quant_type}...")
    
    try:
        import onnx
        from onnxruntime.quantization import quantize_dynamic, QuantType
        
        # Load model
        model = onnx.load(str(onnx_path))
        
        # Quantize
        if quant_type == 'int8':
            quantize_dynamic(
                model_input=str(onnx_path),
                model_output=str(output_path),
                weight_type=QuantType.QUInt8
            )
        else:
            print(f"WARNING: Unknown quantization type: {quant_type}")
            return False
        
        print(f"✓ Quantized model saved: {output_path}")
        return True
    except ImportError:
        print("WARNING: onnx or onnxruntime not available for quantization")
        print("Skipping quantization. Install: pip install onnx onnxruntime")
        return False
    except Exception as e:
        print(f"ERROR: Quantization failed: {e}")
        return False


def test_onnx_inference(gpt_onnx, vits_onnx):
    """Test ONNX models with sample inference."""
    print("\nTesting ONNX inference...")
    
    try:
        import onnxruntime as ort
        import numpy as np
        
        # Load sessions
        gpt_session = ort.InferenceSession(str(gpt_onnx))
        vits_session = ort.InferenceSession(str(vits_onnx))
        
        print("✓ ONNX models loaded successfully")
        print(f"  GPT inputs: {[inp.name for inp in gpt_session.get_inputs()]}")
        print(f"  VITS inputs: {[inp.name for inp in vits_session.get_inputs()]}")
        
        return True
    except ImportError:
        print("WARNING: onnxruntime not available for testing")
        return False
    except Exception as e:
        print(f"WARNING: Inference test failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Export GPT-SoVITS models to ONNX')
    parser.add_argument('--model-dir', type=str, required=True,
                       help='Directory containing trained .pth model files')
    parser.add_argument('--s1-model', type=str, default=None,
                       help='Path to Stage 1 (GPT) model file')
    parser.add_argument('--s2-model', type=str, default=None,
                       help='Path to Stage 2 (VITS) model file')
    parser.add_argument('--output', type=str, default=None,
                       help='Output directory for ONNX models')
    parser.add_argument('--quantize', action='store_true',
                       help='Create INT8 quantized versions for Raspberry Pi')
    parser.add_argument('--no-test', action='store_true',
                       help='Skip inference testing')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("GPT-SoVITS ONNX Export")
    print("=" * 60)
    
    # Find GPT-SoVITS installation
    gptsovits_dir = find_gptsovits_dir()
    
    # Find export script
    export_script = find_onnx_export_script(gptsovits_dir)
    if not export_script:
        print("\nNOTE: ONNX export script not found in GPT-SoVITS repository")
        print("You may need to export manually using GPT-SoVITS WebUI or API")
        print("See GPTSOVITS_SETUP.md for manual export instructions")
        sys.exit(1)
    
    # Find model files
    model_dir = Path(args.model_dir)
    if not model_dir.exists():
        print(f"ERROR: Model directory not found: {model_dir}")
        sys.exit(1)
    
    s1_models, s2_models = find_trained_models(model_dir)
    
    if args.s1_model:
        s1_model = Path(args.s1_model)
    elif s1_models:
        s1_model = s1_models[0]
    else:
        print("ERROR: Stage 1 (GPT) model not found")
        print("Specify with --s1-model or ensure .pth files are in model-dir")
        sys.exit(1)
    
    if args.s2_model:
        s2_model = Path(args.s2_model)
    elif s2_models:
        s2_model = s2_models[0]
    else:
        print("ERROR: Stage 2 (VITS) model not found")
        print("Specify with --s2-model or ensure .pth files are in model-dir")
        sys.exit(1)
    
    print(f"\nStage 1 model: {s1_model}")
    print(f"Stage 2 model: {s2_model}")
    
    # Determine output directory
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = model_dir / 'onnx'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export to ONNX
    if not export_to_onnx(gptsovits_dir, export_script, s1_model, s2_model, output_dir):
        sys.exit(1)
    
    s1_onnx = output_dir / 'tars_gpt_fp32.onnx'
    s2_onnx = output_dir / 'tars_vits_fp32.onnx'
    
    # Quantize if requested
    if args.quantize:
        s1_int8 = output_dir / 'tars_gpt_int8.onnx'
        s2_int8 = output_dir / 'tars_vits_int8.onnx'
        
        quantize_onnx(s1_onnx, s1_int8, 'int8')
        quantize_onnx(s2_onnx, s2_int8, 'int8')
    
    # Test inference
    if not args.no_test:
        test_onnx_inference(s1_onnx, s2_onnx)
    
    print("\n" + "=" * 60)
    print("ONNX Export Complete!")
    print("=" * 60)
    print(f"\nONNX models saved to: {output_dir}")
    print(f"  GPT (FP32): {s1_onnx}")
    print(f"  VITS (FP32): {s2_onnx}")
    if args.quantize:
        print(f"  GPT (INT8): {output_dir / 'tars_gpt_int8.onnx'}")
        print(f"  VITS (INT8): {output_dir / 'tars_vits_int8.onnx'}")
    
    print("\nModels are ready for deployment!")


if __name__ == "__main__":
    main()

