"""Prepare training data for GPT-SoVITS from TARS voice sample."""

import argparse
import os
import sys
import subprocess
from pathlib import Path

# Check for required dependencies
try:
    import librosa
    import soundfile as sf
except ImportError as e:
    print("ERROR: Required dependencies not installed")
    print(f"Missing: {e}")
    print("\nPlease install dependencies first:")
    print("  pip install librosa soundfile")
    print("\nOr run the setup script:")
    print("  python scripts/setup_gptsovits.py")
    sys.exit(1)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Define paths directly to avoid dependency on config.settings
MODELS_DIR = project_root / 'models'
VOICE_SAMPLES_DIR = project_root / 'voice_samples'
TARS_VOICE_SAMPLE = str(VOICE_SAMPLES_DIR / 'tars_sample.wav')


def validate_audio(audio_path):
    """Validate and get audio info."""
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    try:
        y, sr = librosa.load(audio_path, sr=None)
        duration = len(y) / sr
        return y, sr, duration
    except Exception as e:
        raise ValueError(f"Failed to load audio file: {e}")


def convert_audio(audio_path, output_path, target_sr=32000, mono=True):
    """Convert audio to target sample rate and channels."""
    print(f"Loading audio: {audio_path}")
    y, sr, duration = validate_audio(audio_path)
    
    print(f"Original: {sr} Hz, {duration:.2f} seconds")
    
    # Resample if needed
    if sr != target_sr:
        print(f"Resampling to {target_sr} Hz...")
        y = librosa.resample(y, orig_sr=sr, target_sr=target_sr)
    
    # Convert to mono if needed
    if mono and len(y.shape) > 1:
        print("Converting to mono...")
        y = librosa.to_mono(y)
    
    # Save converted audio
    sf.write(output_path, y, target_sr)
    print(f"✓ Saved converted audio: {output_path}")
    
    return output_path


def split_audio(audio_path, output_dir, max_duration=600):
    """Split long audio files into segments."""
    y, sr, duration = validate_audio(audio_path)
    
    if duration <= max_duration:
        print(f"Audio duration ({duration:.2f}s) is within limit, no splitting needed")
        return [audio_path]
    
    print(f"Splitting audio into segments (max {max_duration}s)...")
    segments = []
    segment_duration = max_duration
    num_segments = int(duration / segment_duration) + 1
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for i in range(num_segments):
        start_time = i * segment_duration
        end_time = min((i + 1) * segment_duration, duration)
        
        start_sample = int(start_time * sr)
        end_sample = int(end_time * sr)
        
        segment = y[start_sample:end_sample]
        segment_path = output_dir / f"segment_{i+1:03d}.wav"
        sf.write(segment_path, segment, sr)
        segments.append(str(segment_path))
        print(f"  Segment {i+1}/{num_segments}: {start_time:.1f}s - {end_time:.1f}s")
    
    return segments


def generate_transcript(audio_path):
    """Generate transcript using Whisper ASR."""
    print("Generating transcript using Whisper...")
    
    try:
        from faster_whisper import WhisperModel
        
        model = WhisperModel("base", device="cpu", compute_type="int8")
        segments, info = model.transcribe(str(audio_path), beam_size=5)
        
        transcript = " ".join([segment.text for segment in segments])
        print(f"✓ Generated transcript: {len(transcript)} characters")
        return transcript.strip()
    except ImportError:
        print("WARNING: faster-whisper not available, skipping transcript generation")
        print("You'll need to provide transcripts manually")
        return None
    except Exception as e:
        print(f"WARNING: Failed to generate transcript: {e}")
        return None


def create_dataset_structure(output_dir, audio_files, transcripts=None):
    """Create GPT-SoVITS dataset structure."""
    print(f"\nCreating dataset structure at: {output_dir}")
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create required subdirectories
    raw_dir = output_dir / "raw"
    raw_dir.mkdir(exist_ok=True)
    
    # Copy audio files to raw directory
    for i, audio_file in enumerate(audio_files):
        dest = raw_dir / f"{i+1:04d}.wav"
        import shutil
        shutil.copy2(audio_file, dest)
        print(f"  Copied: {dest.name}")
    
    # Create transcript file if available
    if transcripts:
        transcript_file = output_dir / "transcript.txt"
        with open(transcript_file, 'w', encoding='utf-8') as f:
            for i, transcript in enumerate(transcripts):
                f.write(f"{i+1:04d}|{transcript}\n")
        print(f"✓ Created transcript file: {transcript_file}")
    else:
        print("⚠ No transcripts available. You'll need to create transcript.txt manually.")
        print("  Format: 0001|transcript text here")
    
    print(f"✓ Dataset structure created at: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description='Prepare training data for GPT-SoVITS')
    parser.add_argument('--audio', type=str, default=TARS_VOICE_SAMPLE,
                       help='Path to TARS voice sample WAV file')
    parser.add_argument('--output', type=str, default=None,
                       help='Output directory for dataset (default: models/GPT-SoVITS/dataset/tars)')
    parser.add_argument('--sample-rate', type=int, default=32000,
                       help='Target sample rate (default: 32000)')
    parser.add_argument('--max-duration', type=int, default=600,
                       help='Maximum duration per segment in seconds (default: 600)')
    parser.add_argument('--no-transcript', action='store_true',
                       help='Skip automatic transcript generation')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("GPT-SoVITS Training Data Preparation")
    print("=" * 60)
    
    # Determine output directory
    if args.output:
        output_dir = Path(args.output)
    else:
        gptsovits_dir = MODELS_DIR / 'GPT-SoVITS'
        output_dir = gptsovits_dir / 'dataset' / 'tars'
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Validate input audio
    audio_path = Path(args.audio)
    if not audio_path.exists():
        print(f"ERROR: Audio file not found: {audio_path}")
        sys.exit(1)
    
    # Convert audio to target format
    converted_dir = output_dir / "converted"
    converted_dir.mkdir(exist_ok=True)
    converted_audio = converted_dir / "tars_converted.wav"
    
    convert_audio(str(audio_path), str(converted_audio), 
                  target_sr=args.sample_rate, mono=True)
    
    # Split if needed
    segments = split_audio(str(converted_audio), converted_dir, 
                           max_duration=args.max_duration)
    
    # Generate transcripts
    transcripts = []
    if not args.no_transcript:
        for segment in segments:
            transcript = generate_transcript(segment)
            if transcript:
                transcripts.append(transcript)
            else:
                transcripts.append("")  # Placeholder
    
    # Create dataset structure
    create_dataset_structure(output_dir, segments, 
                           transcripts if transcripts else None)
    
    print("\n" + "=" * 60)
    print("Data preparation complete!")
    print("=" * 60)
    print(f"\nDataset location: {output_dir}")
    print("\nNext step:")
    print("  python scripts/train_gptsovits.py --dataset", output_dir)


if __name__ == "__main__":
    main()

