"""Automated training wrapper for GPT-SoVITS."""

import argparse
import os
import sys
import subprocess
import platform
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Define MODELS_DIR directly to avoid dependency on config.settings
MODELS_DIR = project_root / 'models'


def detect_hardware():
    """Detect available hardware for training."""
    system = platform.system()
    has_cuda = False
    has_mps = False
    
    try:
        import torch
        has_cuda = torch.cuda.is_available()
        if system == "Darwin":
            has_mps = torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False
    except ImportError:
        pass
    
    return system, has_cuda, has_mps


def get_training_config(system, has_cuda, has_mps):
    """Get training configuration based on hardware."""
    if system == "Windows" and has_cuda:
        return {
            'batch_size': 4,
            'epochs': 30,
            'device': 'cuda',
            'description': 'Windows with NVIDIA GPU'
        }
    elif system == "Darwin" and has_mps:
        return {
            'batch_size': 2,
            'epochs': 20,
            'device': 'mps',
            'description': 'macOS with Apple Silicon (MPS)'
        }
    else:
        print("WARNING: No GPU detected. Training will be very slow on CPU.")
        print("Consider using a GPU-enabled machine or cloud service.")
        response = input("Continue with CPU training? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
        return {
            'batch_size': 1,
            'epochs': 10,
            'device': 'cpu',
            'description': 'CPU only (not recommended)'
        }


def find_gptsovits_dir():
    """Find GPT-SoVITS installation directory."""
    gptsovits_dir = MODELS_DIR / 'GPT-SoVITS'
    if not gptsovits_dir.exists():
        print(f"ERROR: GPT-SoVITS not found at {gptsovits_dir}")
        print("Run setup first: python scripts/setup_gptsovits.py")
        sys.exit(1)
    return gptsovits_dir


def train_stage1(gptsovits_dir, dataset_dir, config, output_dir):
    """Train Stage 1: GPT model (prosody/rhythm)."""
    print("\n" + "=" * 60)
    print("Stage 1: Training GPT Model (Prosody)")
    print("=" * 60)
    
    # GPT-SoVITS training scripts are in GPT_SoVITS/ subdirectory
    gpt_sovits_dir = gptsovits_dir / 'GPT_SoVITS'
    train_script = gpt_sovits_dir / 's1_train.py'
    
    if not train_script.exists():
        print("ERROR: Could not find GPT-SoVITS Stage 1 training script")
        print(f"Expected at: {train_script}")
        print("\nGPT-SoVITS training requires:")
        print("1. Preprocessed dataset (semantic tokens, phonemes)")
        print("2. Config file (YAML)")
        print("3. Pre-trained base models")
        print("\nFor automated training, consider using GPT-SoVITS WebUI:")
        print("  cd models/GPT-SoVITS")
        print("  python webui.py")
        print("\nOr follow the manual training guide in GPTSOVITS_SETUP.md")
        sys.exit(1)
    
    # Check if dataset needs preprocessing
    # GPT-SoVITS requires semantic tokens and phonemes, not just raw audio
    print("\n⚠ NOTE: GPT-SoVITS training requires preprocessing the dataset first.")
    print("The dataset needs:")
    print("  - Semantic tokens (generated from audio)")
    print("  - Phonemes (generated from text)")
    print("  - Pre-trained base models")
    print("\nThis script provides a simplified interface, but full training")
    print("may require using GPT-SoVITS WebUI or following their documentation.")
    print("\nFor now, we'll attempt to use the training script with a config file...")
    
    # Create or modify config file
    config_file = gpt_sovits_dir / 'configs' / 's1.yaml'
    if not config_file.exists():
        print(f"ERROR: Config file not found: {config_file}")
        print("Please ensure GPT-SoVITS is properly set up")
        sys.exit(1)
    
    # Prepare training command
    # GPT-SoVITS s1_train.py takes --config_file argument
    cmd = [
        sys.executable, str(train_script),
        '--config_file', str(config_file)
    ]
    
    print(f"\nRunning: {' '.join(cmd)}")
    print(f"Working directory: {gpt_sovits_dir}")
    print(f"Device: {config['device']}")
    print(f"Batch size: {config['batch_size']} (set in config file)")
    print(f"Epochs: {config['epochs']} (set in config file)")
    print("\n⚠ IMPORTANT: Make sure you've:")
    print("  1. Preprocessed your dataset (run prepare_datasets scripts)")
    print("  2. Downloaded pre-trained base models")
    print("  3. Updated config file with correct paths")
    print("\nThis may take 30 minutes to 2 hours depending on hardware...")
    
    response = input("\nContinue with training? (y/n): ")
    if response.lower() != 'y':
        print("Training cancelled")
        return False
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, cwd=str(gpt_sovits_dir), check=True)
        elapsed = time.time() - start_time
        print(f"\n✓ Stage 1 training completed in {elapsed/60:.1f} minutes")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Stage 1 training failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure dataset is preprocessed (semantic tokens, phonemes)")
        print("2. Check config file paths are correct")
        print("3. Verify pre-trained models are downloaded")
        print("4. Try using GPT-SoVITS WebUI for easier training")
        return False
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user")
        return False


def train_stage2(gptsovits_dir, dataset_dir, config, output_dir, s1_model_path):
    """Train Stage 2: VITS model (waveform synthesis)."""
    print("\n" + "=" * 60)
    print("Stage 2: Training VITS Model (Waveform Synthesis)")
    print("=" * 60)
    
    # GPT-SoVITS training scripts are in GPT_SoVITS/ subdirectory
    gpt_sovits_dir = gptsovits_dir / 'GPT_SoVITS'
    train_script = gpt_sovits_dir / 's2_train.py'
    
    if not train_script.exists():
        print("ERROR: Could not find GPT-SoVITS Stage 2 training script")
        print(f"Expected at: {train_script}")
        sys.exit(1)
    
    print(f"\nUsing Stage 1 model: {s1_model_path}")
    print("⚠ NOTE: Stage 2 training uses config from utils.get_hparams()")
    print("You may need to configure this in GPT-SoVITS config system")
    
    # Stage 2 training uses a different system (utils.get_hparams)
    # This is more complex and may require manual configuration
    cmd = [
        sys.executable, str(train_script)
    ]
    
    print(f"\nRunning: {' '.join(cmd)}")
    print(f"Working directory: {gpt_sovits_dir}")
    print("\nThis may take 30 minutes to 2 hours...")
    
    response = input("\nContinue with Stage 2 training? (y/n): ")
    if response.lower() != 'y':
        print("Training cancelled")
        return False
    
    start_time = time.time()
    
    try:
        result = subprocess.run(cmd, cwd=str(gpt_sovits_dir), check=True)
        elapsed = time.time() - start_time
        print(f"\n✓ Stage 2 training completed in {elapsed/60:.1f} minutes")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\nERROR: Stage 2 training failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Stage 1 model is properly trained")
        print("2. Check config file paths")
        print("3. Verify dataset is properly formatted")
        print("4. Consider using GPT-SoVITS WebUI for easier training")
        return False
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user")
        return False


def find_trained_models(output_dir):
    """Find trained model files."""
    s1_models = list(output_dir.glob('**/s1*.pth'))
    s2_models = list(output_dir.glob('**/s2*.pth'))
    
    # Also check common GPT-SoVITS output locations
    if not s1_models:
        s1_models = list(output_dir.glob('**/gpt*.pth'))
    if not s2_models:
        s2_models = list(output_dir.glob('**/vits*.pth'))
    
    return s1_models, s2_models


def main():
    parser = argparse.ArgumentParser(description='Train GPT-SoVITS model')
    parser.add_argument('--dataset', type=str, required=True,
                       help='Path to prepared dataset directory')
    parser.add_argument('--audio', type=str, default=None,
                       help='Path to audio file (will prepare data if dataset not provided)')
    parser.add_argument('--output', type=str, default=None,
                       help='Output directory for trained models')
    parser.add_argument('--batch-size', type=int, default=None,
                       help='Batch size (auto-detected if not specified)')
    parser.add_argument('--epochs', type=int, default=None,
                       help='Number of epochs (auto-detected if not specified)')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("GPT-SoVITS Training")
    print("=" * 60)
    
    # Handle audio file input (prepare data first)
    if args.audio and not args.dataset:
        print("Preparing training data from audio file...")
        from scripts.prepare_training_data import main as prepare_main
        # This would need to be called programmatically
        print("Please run: python scripts/prepare_training_data.py --audio", args.audio)
        print("Then run this script again with --dataset")
        sys.exit(1)
    
    # Find GPT-SoVITS installation
    gptsovits_dir = find_gptsovits_dir()
    
    # Detect hardware
    system, has_cuda, has_mps = detect_hardware()
    config = get_training_config(system, has_cuda, has_mps)
    
    print(f"\nHardware: {config['description']}")
    
    # Override config if specified
    if args.batch_size:
        config['batch_size'] = args.batch_size
    if args.epochs:
        config['epochs'] = args.epochs
    
    # Determine dataset and output directories
    dataset_dir = Path(args.dataset)
    if not dataset_dir.exists():
        print(f"ERROR: Dataset directory not found: {dataset_dir}")
        sys.exit(1)
    
    # Warn about GPT-SoVITS training complexity
    print("\n" + "=" * 60)
    print("IMPORTANT: GPT-SoVITS Training Notes")
    print("=" * 60)
    print("\nGPT-SoVITS training is complex and requires:")
    print("1. Preprocessed dataset (semantic tokens, phonemes)")
    print("2. Pre-trained base models")
    print("3. Properly configured YAML files")
    print("\nFor easier training, consider using GPT-SoVITS WebUI:")
    print("  cd models/GPT-SoVITS")
    print("  python webui.py")
    print("\nThis script provides a basic wrapper but may require")
    print("manual configuration of GPT-SoVITS settings.")
    print("=" * 60)
    
    response = input("\nContinue anyway? (y/n): ")
    if response.lower() != 'y':
        print("Training cancelled. Consider using WebUI for easier setup.")
        sys.exit(0)
    
    if args.output:
        output_dir = Path(args.output)
    else:
        output_dir = MODELS_DIR / 'gptsovits_models' / 'tars_voice'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"\nDataset: {dataset_dir}")
    print(f"Output: {output_dir}")
    
    # Train Stage 1
    if not train_stage1(gptsovits_dir, dataset_dir, config, output_dir):
        sys.exit(1)
    
    # Find Stage 1 model
    s1_models, _ = find_trained_models(output_dir)
    if not s1_models:
        print("ERROR: Stage 1 model not found after training")
        sys.exit(1)
    
    s1_model = s1_models[0]  # Use first found model
    print(f"\nStage 1 model: {s1_model}")
    
    # Train Stage 2
    if not train_stage2(gptsovits_dir, dataset_dir, config, output_dir, s1_model):
        sys.exit(1)
    
    # Find final models
    s1_models, s2_models = find_trained_models(output_dir)
    
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print(f"\nTrained models saved to: {output_dir}")
    if s1_models:
        print(f"Stage 1 (GPT) model: {s1_models[0]}")
    if s2_models:
        print(f"Stage 2 (VITS) model: {s2_models[0]}")
    
    print("\nNext step:")
    print("  python scripts/export_onnx.py --model-dir", output_dir)


if __name__ == "__main__":
    main()

