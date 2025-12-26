"""Setup script for GPT-SoVITS installation with platform detection."""

import os
import sys
import subprocess
import platform
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Define MODELS_DIR directly to avoid dependency on config.settings
MODELS_DIR = project_root / 'models'


def check_venv():
    """Check if running in a virtual environment."""
    return hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)


def detect_platform():
    """Detect platform and hardware capabilities."""
    system = platform.system()
    has_cuda = False
    has_mps = False
    
    # Try to detect hardware, but don't fail if PyTorch isn't installed yet
    if system == "Windows":
        try:
            import torch
            has_cuda = torch.cuda.is_available()
        except ImportError:
            pass
    elif system == "Darwin":
        # On macOS, assume MPS is available if Apple Silicon (will verify after PyTorch install)
        # Check for Apple Silicon by looking at architecture
        import platform as plat
        machine = plat.machine()
        if machine == 'arm64':
            has_mps = True  # Likely available, will verify after install
        try:
            import torch
            has_mps = torch.backends.mps.is_available() if hasattr(torch.backends, 'mps') else False
        except ImportError:
            pass
    
    return system, has_cuda, has_mps


def check_git():
    """Check if git is installed."""
    try:
        subprocess.run(['git', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def clone_gptsovits():
    """Clone GPT-SoVITS repository."""
    gptsovits_dir = MODELS_DIR / 'GPT-SoVITS'
    
    if gptsovits_dir.exists():
        print(f"GPT-SoVITS directory already exists: {gptsovits_dir}")
        print("Skipping clone. Delete the directory if you want to re-clone.")
        return gptsovits_dir
    
    if not check_git():
        print("ERROR: git is not installed. Please install git first.")
        sys.exit(1)
    
    print("Cloning GPT-SoVITS repository...")
    repo_url = "https://github.com/RVC-Boss/GPT-SoVITS.git"
    
    try:
        subprocess.run(
            ['git', 'clone', repo_url, str(gptsovits_dir)],
            check=True,
            cwd=str(MODELS_DIR)
        )
        print(f"✓ GPT-SoVITS cloned to {gptsovits_dir}")
        return gptsovits_dir
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to clone GPT-SoVITS: {e}")
        sys.exit(1)


def install_pytorch(system, has_cuda, has_mps):
    """Install platform-specific PyTorch."""
    print("\nInstalling PyTorch...")
    
    # Check if in virtual environment
    if not check_venv():
        print("WARNING: Not running in a virtual environment")
        print("macOS requires a virtual environment for package installation")
        print("\nPlease create and activate a virtual environment first:")
        print("  python3 -m venv venv")
        print("  source venv/bin/activate")
        print("  python3 scripts/setup_gptsovits.py")
        print("\nOr continue anyway (may require --break-system-packages flag)")
        response = input("\nContinue anyway? (y/n): ")
        if response.lower() != 'y':
            sys.exit(0)
    
    if system == "Windows" and has_cuda:
        print("Detected Windows with CUDA support")
        cmd = [
            sys.executable, '-m', 'pip', 'install',
            'torch', 'torchvision', 'torchaudio',
            '--index-url', 'https://download.pytorch.org/whl/cu118'
        ]
    elif system == "Darwin":
        # On macOS, always try MPS-capable PyTorch (works on both Intel and Apple Silicon)
        print("Detected macOS (will use MPS if available on Apple Silicon)")
        cmd = [
            sys.executable, '-m', 'pip', 'install',
            'torch', 'torchvision', 'torchaudio'
        ]
    else:
        print("Detected CPU-only system")
        cmd = [
            sys.executable, '-m', 'pip', 'install',
            'torch', 'torchvision', 'torchaudio',
            '--index-url', 'https://download.pytorch.org/whl/cpu'
        ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("✓ PyTorch installed")
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr if e.stderr else str(e)
        if "externally-managed-environment" in error_msg:
            print("\nERROR: Python environment is externally managed (macOS Homebrew)")
            print("\nPlease use a virtual environment:")
            print("  1. Create venv: python3 -m venv venv")
            print("  2. Activate: source venv/bin/activate")
            print("  3. Run setup again: python3 scripts/setup_gptsovits.py")
            print("\nOr install with --break-system-packages (not recommended):")
            print(f"  {' '.join(cmd)} --break-system-packages")
        else:
            print(f"ERROR: Failed to install PyTorch: {error_msg}")
        sys.exit(1)


def install_gptsovits_deps(gptsovits_dir):
    """Install GPT-SoVITS dependencies."""
    print("\nInstalling GPT-SoVITS dependencies...")
    
    requirements_file = gptsovits_dir / 'requirements.txt'
    if not requirements_file.exists():
        print(f"WARNING: requirements.txt not found at {requirements_file}")
        print("Installing common dependencies manually...")
        common_deps = [
            'librosa>=0.10.0',
            'soundfile>=0.12.0',
            'audioread>=3.0.0',
            'cn2an>=0.5.17',
            'jieba>=0.42.1',
            'onnx>=1.15.0',
            'onnxruntime>=1.16.0',
            'ffmpeg-python>=0.2.0',
            'numpy>=1.24.0',
            'scipy>=1.11.0',
            'phonemizer>=3.2.1',
            'pyyaml>=6.0',
            'tqdm>=4.66.0',
            'pytorch-lightning>=2.0.0',  # Required for training
        ]
        for dep in common_deps:
            try:
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', dep],
                    check=True,
                    capture_output=True,
                    text=True
                )
            except subprocess.CalledProcessError as e:
                if "externally-managed-environment" in (e.stderr or ""):
                    print(f"WARNING: Cannot install {dep} - need virtual environment")
                else:
                    print(f"WARNING: Failed to install {dep}")
    else:
        try:
            print(f"Installing from {requirements_file}...")
            print("This may take several minutes...")
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', '-r', str(requirements_file)],
                check=True,
                capture_output=False  # Show output so user can see progress
            )
            print("✓ GPT-SoVITS dependencies installed")
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            if "externally-managed-environment" in error_msg:
                print("WARNING: Cannot install dependencies - need virtual environment")
                print("Please create and activate a venv, then run setup again")
            else:
                print(f"WARNING: Some dependencies may have failed: {error_msg}")
                print("You may need to install them manually")
                print("\nTrying to install critical dependencies individually...")
                # Install critical dependencies that might have failed
                critical_deps = [
                    'pytorch-lightning>=2.4',
                    'transformers>=4.43,<=4.50',
                    'gradio<5',
                    'tensorboard',
                ]
                for dep in critical_deps:
                    try:
                        print(f"Installing {dep}...")
                        subprocess.run(
                            [sys.executable, '-m', 'pip', 'install', dep],
                            check=True,
                            capture_output=False
                        )
                        print(f"✓ Installed {dep}")
                    except Exception as install_error:
                        print(f"⚠ Failed to install {dep}: {install_error}")
                print("\nYou may need to install remaining dependencies manually:")
                print(f"  pip install -r {requirements_file}")


def verify_installation():
    """Verify installation and test GPU availability."""
    print("\nVerifying installation...")
    
    try:
        import torch
        print(f"✓ PyTorch version: {torch.__version__}")
        
        if torch.cuda.is_available():
            print(f"✓ CUDA available: {torch.cuda.get_device_name(0)}")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            print("✓ MPS (Metal) available on macOS - GPU acceleration enabled")
        else:
            print("⚠ Using CPU (no GPU acceleration)")
            if platform.system() == "Darwin":
                import platform as plat
                if plat.machine() == 'arm64':
                    print("  Note: MPS should be available on Apple Silicon")
                    print("  If MPS is not available, PyTorch may need to be reinstalled")
        
    except ImportError as e:
        print(f"ERROR: Missing dependency: {e}")
        print("Some dependencies may need to be installed manually")
        return False
    
    try:
        import onnxruntime as ort
        print(f"✓ ONNX Runtime version: {ort.__version__}")
    except ImportError:
        print("⚠ ONNX Runtime not installed (will be installed with GPT-SoVITS deps)")
    
    try:
        import librosa
        print(f"✓ librosa version: {librosa.__version__}")
    except ImportError:
        print("⚠ librosa not installed (will be installed with GPT-SoVITS deps)")
    
    print("\n✓ Installation verification complete!")
    return True


def download_base_models(gptsovits_dir):
    """Download pre-trained base models for fine-tuning."""
    print("\nChecking for base models...")
    
    # GPT-SoVITS typically requires downloading base models
    # This is usually done during first training run
    # We'll just check if the models directory exists
    models_dir = gptsovits_dir / 'pretrained_models'
    if not models_dir.exists():
        print("Base models will be downloaded during first training run.")
        print("This may take some time and require internet connection.")
    else:
        print("✓ Base models directory exists")


def main():
    """Main setup function."""
    print("=" * 60)
    print("GPT-SoVITS Setup")
    print("=" * 60)
    
    system, has_cuda, has_mps = detect_platform()
    print(f"\nPlatform: {system}")
    print(f"CUDA available: {has_cuda}")
    print(f"MPS available: {has_mps}")
    
    # Create models directory if it doesn't exist
    MODELS_DIR.mkdir(exist_ok=True)
    
    # Clone repository
    gptsovits_dir = clone_gptsovits()
    
    # Install PyTorch
    install_pytorch(system, has_cuda, has_mps)
    
    # Install dependencies
    install_gptsovits_deps(gptsovits_dir)
    
    # Download base models (info only)
    download_base_models(gptsovits_dir)
    
    # Verify installation
    if not verify_installation():
        print("\n⚠ Some dependencies may be missing. Continuing with setup...")
    
    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print(f"\nGPT-SoVITS is installed at: {gptsovits_dir}")
    
    if not check_venv():
        print("\n⚠ NOTE: You're not in a virtual environment.")
        print("Consider using a venv for better dependency management:")
        print("  python3 -m venv venv")
        print("  source venv/bin/activate")
    
    print("\nNext steps:")
    print("1. Prepare training data: python scripts/prepare_training_data.py")
    print("2. Train model: python scripts/train_gptsovits.py --audio voice_samples/tars_sample.wav")
    print("3. Export ONNX: python scripts/export_onnx.py")


if __name__ == "__main__":
    main()

