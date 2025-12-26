"""Helper script to extract TARS audio from video files."""

import os
import sys
from pathlib import Path

def extract_audio_ffmpeg(video_path: str, output_path: str, start_time: str = None, duration: str = None):
    """
    Extract audio from video using FFmpeg.
    
    Args:
        video_path: Path to video file
        output_path: Path to save audio file
        start_time: Start time (HH:MM:SS format)
        duration: Duration (HH:MM:SS format)
    """
    try:
        import subprocess
        
        cmd = ['ffmpeg', '-i', video_path]
        
        if start_time:
            cmd.extend(['-ss', start_time])
        if duration:
            cmd.extend(['-t', duration])
        
        cmd.extend(['-vn', '-acodec', 'pcm_s16le', '-ar', '22050', '-ac', '1', output_path])
        
        print(f"Extracting audio: {video_path} -> {output_path}")
        subprocess.run(cmd, check=True)
        print(f"Audio extracted successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error extracting audio: {e}")
        print("Make sure FFmpeg is installed: https://ffmpeg.org/download.html")
    except FileNotFoundError:
        print("FFmpeg not found. Install FFmpeg first:")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        print("  Or use: choco install ffmpeg")

def extract_audio_moviepy(video_path: str, output_path: str):
    """
    Extract audio from video using moviepy.
    
    Args:
        video_path: Path to video file
        output_path: Path to save audio file
    """
    try:
        from moviepy.video.io.VideoFileClip import VideoFileClip
        
        print(f"Extracting audio: {video_path} -> {output_path}")
        video = VideoFileClip(video_path)
        audio = video.audio
        audio.write_audiofile(output_path, fps=22050, nbytes=2, codec='pcm_s16le')
        audio.close()
        video.close()
        print(f"Audio extracted successfully!")
        
    except ImportError:
        print("moviepy not installed. Install with: pip install moviepy")
    except Exception as e:
        print(f"Error extracting audio: {e}")

def convert_mp3_to_wav_ffmpeg(mp3_path: str, output_path: str, start_time: str = None, duration: str = None):
    """
    Convert MP3 file to WAV format using FFmpeg.
    
    Args:
        mp3_path: Path to MP3 file
        output_path: Path to save WAV file
        start_time: Start time (HH:MM:SS format)
        duration: Duration (HH:MM:SS format)
    """
    try:
        import subprocess
        
        cmd = ['ffmpeg', '-i', mp3_path]
        
        if start_time:
            cmd.extend(['-ss', start_time])
        if duration:
            cmd.extend(['-t', duration])
        
        cmd.extend(['-acodec', 'pcm_s16le', '-ar', '22050', '-ac', '1', output_path])
        
        print(f"Converting MP3: {mp3_path} -> {output_path}")
        subprocess.run(cmd, check=True)
        print(f"MP3 converted successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"Error converting MP3: {e}")
        print("Make sure FFmpeg is installed: https://ffmpeg.org/download.html")
        raise
    except FileNotFoundError:
        print("FFmpeg not found. Install FFmpeg first:")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        print("  Or use: choco install ffmpeg")
        raise

def convert_mp3_to_wav_moviepy(mp3_path: str, output_path: str):
    """
    Convert MP3 file to WAV format using moviepy.
    
    Args:
        mp3_path: Path to MP3 file
        output_path: Path to save WAV file
    """
    try:
        from moviepy.audio.io.AudioFileClip import AudioFileClip
        
        print(f"Converting MP3: {mp3_path} -> {output_path}")
        audio = AudioFileClip(mp3_path)
        audio.write_audiofile(output_path, fps=22050, nbytes=2, codec='pcm_s16le')
        audio.close()
        print(f"MP3 converted successfully!")
        
    except ImportError:
        print("moviepy not installed. Install with: pip install moviepy")
        raise
    except Exception as e:
        print(f"Error converting MP3: {e}")
        raise

def combine_audio_files_ffmpeg(input_files: list, output_path: str):
    """
    Combine multiple audio files into one WAV file using FFmpeg.
    
    Args:
        input_files: List of paths to audio files (MP3, WAV, etc.)
        output_path: Path to save combined WAV file
    """
    try:
        import subprocess
        import tempfile
        
        if not input_files:
            raise ValueError("No input files provided")
        
        for file_path in input_files:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Input file not found: {file_path}")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            concat_file = f.name
            for file_path in input_files:
                abs_path = os.path.abspath(file_path).replace('\\', '/')
                f.write(f"file '{abs_path}'\n")
        
        try:
            cmd = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', concat_file,
                   '-acodec', 'pcm_s16le', '-ar', '22050', '-ac', '1', output_path]
            
            print(f"Combining {len(input_files)} audio files -> {output_path}")
            subprocess.run(cmd, check=True)
            print(f"Audio files combined successfully!")
        finally:
            if os.path.exists(concat_file):
                os.unlink(concat_file)
        
    except subprocess.CalledProcessError as e:
        print(f"Error combining audio files: {e}")
        print("Make sure FFmpeg is installed: https://ffmpeg.org/download.html")
        raise
    except FileNotFoundError as e:
        print(f"FFmpeg not found: {e}")
        print("Install FFmpeg first:")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        print("  Or use: choco install ffmpeg")
        raise

def combine_audio_files_moviepy(input_files: list, output_path: str):
    """
    Combine multiple audio files into one WAV file using moviepy.
    
    Args:
        input_files: List of paths to audio files
        output_path: Path to save combined WAV file
    """
    try:
        from moviepy.audio.io.AudioFileClip import AudioFileClip
        from moviepy.audio.AudioClip import concatenate_audioclips
        
        if not input_files:
            raise ValueError("No input files provided")
        
        print(f"Combining {len(input_files)} audio files -> {output_path}")
        clips = []
        for file_path in input_files:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Input file not found: {file_path}")
            clips.append(AudioFileClip(file_path))
        
        final_clip = concatenate_audioclips(clips)
        final_clip.write_audiofile(output_path, fps=22050, nbytes=2, codec='pcm_s16le')
        
        for clip in clips:
            clip.close()
        final_clip.close()
        
        print(f"Audio files combined successfully!")
        
    except ImportError:
        print("moviepy not installed. Install with: pip install moviepy")
        raise
    except Exception as e:
        print(f"Error combining audio files: {e}")
        raise

def main():
    """Main function."""
    print("TARS Audio Extraction Helper")
    print("=" * 40)
    
    if len(sys.argv) < 3:
        print("Usage:")
        print("  Single file:")
        print("    python extract_tars_audio.py <video_file|mp3_file> <output_wav> [start_time] [duration]")
        print("")
        print("  Combine multiple files:")
        print("    python extract_tars_audio.py combine <output_wav> <file1> <file2> [file3] ...")
        print("")
        print("Examples:")
        print("  python extract_tars_audio.py interstellar.mp4 tars_clip1.wav 01:23:45 00:00:30")
        print("  python extract_tars_audio.py audio.mp3 tars_clip1.wav 00:00:10 00:00:30")
        print("  python extract_tars_audio.py combine tars_combined.wav clip1.mp3 clip2.mp3 clip3.wav")
        print("")
        print("Note: For voice cloning, you need at least 6 seconds of audio.")
        return
    
    if sys.argv[1].lower() == 'combine':
        if len(sys.argv) < 4:
            print("Error: combine mode requires at least 2 input files")
            print("Usage: python extract_tars_audio.py combine <output_wav> <file1> <file2> [file3] ...")
            return
        
        output_path = sys.argv[2]
        input_files = sys.argv[3:]
        
        try:
            combine_audio_files_ffmpeg(input_files, output_path)
        except Exception as e:
            print(f"FFmpeg not available, trying moviepy... (Error: {e})")
            try:
                combine_audio_files_moviepy(input_files, output_path)
            except Exception as e:
                print(f"Failed to combine audio files: {e}")
                print("Please install FFmpeg or moviepy.")
        return
    
    input_path = sys.argv[1]
    output_path = sys.argv[2]
    start_time = sys.argv[3] if len(sys.argv) > 3 else None
    duration = sys.argv[4] if len(sys.argv) > 4 else None
    
    if not os.path.exists(input_path):
        print(f"Error: Input file not found: {input_path}")
        return
    
    input_ext = Path(input_path).suffix.lower()
    
    if input_ext == '.mp3':
        try:
            convert_mp3_to_wav_ffmpeg(input_path, output_path, start_time, duration)
        except:
            print("FFmpeg not available, trying moviepy...")
            try:
                convert_mp3_to_wav_moviepy(input_path, output_path)
            except:
                print("Failed to convert MP3 file. Please install FFmpeg or moviepy.")
    else:
        try:
            extract_audio_ffmpeg(input_path, output_path, start_time, duration)
        except:
            print("FFmpeg not available, trying moviepy...")
            try:
                extract_audio_moviepy(input_path, output_path)
            except:
                print("Failed to extract audio. Please install FFmpeg or moviepy.")

if __name__ == "__main__":
    main()

