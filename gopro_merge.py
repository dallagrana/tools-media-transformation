#!/usr/bin/env python3
"""
GoPro Video Merger with NVENC Hardware Acceleration
Merges GoPro footage in chronological order using NVIDIA GPU encoding
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple


class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_header(text: str):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")


def print_success(text: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_error(text: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def print_info(text: str):
    """Print info message"""
    print(f"{Colors.CYAN}ℹ {text}{Colors.END}")


def check_dependencies():
    """Check if required tools are installed"""
    print_info("Checking dependencies...")
    
    # Check FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              check=True)
        if 'nvenc' not in result.stdout.lower():
            print_error("FFmpeg found but NVENC support not detected!")
            print_info("Make sure FFmpeg is compiled with --enable-nvenc")
            return False
        print_success("FFmpeg with NVENC support found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("FFmpeg not found! Please install FFmpeg with NVENC support.")
        return False
    
    # Check FFprobe
    try:
        subprocess.run(['ffprobe', '-version'], 
                      capture_output=True, 
                      check=True)
        print_success("FFprobe found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_error("FFprobe not found! Please install FFmpeg package.")
        return False
    
    return True


def get_video_metadata(filepath: Path) -> Dict:
    """Extract metadata from video file using ffprobe"""
    try:
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(filepath)
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        metadata = json.loads(result.stdout)
        
        # Get creation time from metadata or file stats
        creation_time = None
        if 'format' in metadata and 'tags' in metadata['format']:
            tags = metadata['format']['tags']
            # Try different tag names
            for tag in ['creation_time', 'date', 'com.apple.quicktime.creationdate']:
                if tag in tags:
                    try:
                        creation_time = datetime.fromisoformat(tags[tag].replace('Z', '+00:00'))
                        break
                    except:
                        pass
        
        # Fallback to file modification time
        if not creation_time:
            creation_time = datetime.fromtimestamp(filepath.stat().st_mtime)
        
        # Get video duration
        duration = float(metadata['format']['duration'])
        
        # Get video stream info
        video_stream = next((s for s in metadata['streams'] if s['codec_type'] == 'video'), None)
        
        return {
            'filepath': filepath,
            'creation_time': creation_time,
            'duration': duration,
            'width': video_stream.get('width', 0) if video_stream else 0,
            'height': video_stream.get('height', 0) if video_stream else 0,
            'codec': video_stream.get('codec_name', 'unknown') if video_stream else 'unknown',
            'fps': eval(video_stream.get('r_frame_rate', '30/1')) if video_stream else 30
        }
    except Exception as e:
        print_error(f"Error reading metadata from {filepath.name}: {e}")
        return None


def find_gopro_videos(directory: Path) -> List[Dict]:
    """Find all GoPro video files and sort by creation time"""
    print_info(f"Scanning directory: {directory}")
    
    video_files = []
    extensions = {'.mp4', '.MP4'}
    
    for filepath in directory.iterdir():
        if filepath.is_file() and filepath.suffix in extensions:
            metadata = get_video_metadata(filepath)
            if metadata:
                video_files.append(metadata)
                print(f"  Found: {filepath.name} - {metadata['creation_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Sort by creation time
    video_files.sort(key=lambda x: x['creation_time'])
    
    return video_files


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_user_choices() -> Dict:
    """Interactive menu for encoding options"""
    print_header("ENCODING OPTIONS")
    
    choices = {}
    
    # Hardware encoding
    print(f"{Colors.BOLD}Encoding method:{Colors.END}")
    print("  1. NVIDIA NVENC (Hardware - Recommended)")
    print("  2. CPU (Software - Slower)")
    hw_choice = input(f"{Colors.CYAN}Select [1-2] (default: 1): {Colors.END}").strip() or "1"
    choices['use_nvenc'] = hw_choice == "1"
    
    # Codec
    print(f"\n{Colors.BOLD}Output codec:{Colors.END}")
    if choices['use_nvenc']:
        print("  1. H.264 (h264_nvenc) - Best compatibility")
        print("  2. H.265/HEVC (hevc_nvenc) - Better compression")
        print("  3. AV1 (av1_nvenc) - Newest, best quality/size")
    else:
        print("  1. H.264 (libx264)")
        print("  2. H.265/HEVC (libx265)")
    codec_choice = input(f"{Colors.CYAN}Select [1-3] (default: 1): {Colors.END}").strip() or "1"
    
    if choices['use_nvenc']:
        codec_map = {'1': 'h264_nvenc', '2': 'hevc_nvenc', '3': 'av1_nvenc'}
    else:
        codec_map = {'1': 'libx264', '2': 'libx265'}
    choices['codec'] = codec_map.get(codec_choice, codec_map['1'])
    
    # Resolution
    print(f"\n{Colors.BOLD}Output resolution:{Colors.END}")
    print("  1. 4K (3840x2160)")
    print("  2. 2K (2560x1440)")
    print("  3. 1080p (1920x1080)")
    print("  4. 720p (1280x720)")
    print("  5. Keep original")
    res_choice = input(f"{Colors.CYAN}Select [1-5] (default: 5): {Colors.END}").strip() or "5"
    res_map = {
        '1': '3840:2160',
        '2': '2560:1440',
        '3': '1920:1080',
        '4': '1280:720',
        '5': None
    }
    choices['resolution'] = res_map.get(res_choice)
    
    # Frame rate
    print(f"\n{Colors.BOLD}Output frame rate:{Colors.END}")
    print("  1. 60 fps")
    print("  2. 30 fps")
    print("  3. Keep original")
    fps_choice = input(f"{Colors.CYAN}Select [1-3] (default: 3): {Colors.END}").strip() or "3"
    fps_map = {'1': '60', '2': '30', '3': None}
    choices['fps'] = fps_map.get(fps_choice)
    
    # Stabilization
    print(f"\n{Colors.BOLD}Video stabilization:{Colors.END}")
    print("  1. Yes (vidstabdetect + vidstabtransform)")
    print("  2. No")
    stab_choice = input(f"{Colors.CYAN}Select [1-2] (default: 2): {Colors.END}").strip() or "2"
    choices['stabilization'] = stab_choice == "1"
    
    # Quality preset (for NVENC)
    if choices['use_nvenc']:
        print(f"\n{Colors.BOLD}Encoding preset (quality vs speed):{Colors.END}")
        print("  1. p1 (fastest, lower quality)")
        print("  2. p4 (balanced)")
        print("  3. p7 (slower, best quality)")
        preset_choice = input(f"{Colors.CYAN}Select [1-3] (default: 2): {Colors.END}").strip() or "2"
        preset_map = {'1': 'p1', '2': 'p4', '3': 'p7'}
        choices['preset'] = preset_map.get(preset_choice, 'p4')
    else:
        choices['preset'] = 'medium'
    
    # Bitrate
    print(f"\n{Colors.BOLD}Bitrate (Mbps):{Colors.END}")
    bitrate = input(f"{Colors.CYAN}Enter bitrate in Mbps (default: 50): {Colors.END}").strip() or "50"
    choices['bitrate'] = f"{bitrate}M"
    
    return choices


def create_concat_file(video_files: List[Dict], output_dir: Path) -> Path:
    """Create FFmpeg concat file for merging"""
    concat_file = output_dir / "concat_list.txt"
    
    with open(concat_file, 'w') as f:
        for video in video_files:
            # Use absolute paths and escape special characters
            filepath = str(video['filepath'].absolute()).replace("'", "'\\''")
            f.write(f"file '{filepath}'\n")
    
    return concat_file


def merge_videos(video_files: List[Dict], output_dir: Path, choices: Dict):
    """Merge videos using FFmpeg with NVENC"""
    
    # Create output directory
    output_dir.mkdir(exist_ok=True)
    
    # Generate output filename
    first_date = video_files[0]['creation_time'].strftime('%Y%m%d')
    codec_name = choices['codec'].replace('_nvenc', '').replace('lib', '')
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f"gopro_merged_{first_date}_{codec_name}_{timestamp}.mp4"
    
    # Create concat file
    concat_file = create_concat_file(video_files, output_dir)
    
    print_header("STARTING VIDEO MERGE")
    print_info(f"Output file: {output_file.name}")
    print_info(f"Number of clips: {len(video_files)}")
    total_duration = sum(v['duration'] for v in video_files)
    print_info(f"Total duration: {format_duration(total_duration)}")
    print()
    
    # Build FFmpeg command
    cmd = ['ffmpeg', '-y']
    
    # Input
    cmd.extend(['-f', 'concat', '-safe', '0', '-i', str(concat_file)])
    
    # Video filters
    vfilters = []
    
    # Stabilization (if requested)
    if choices['stabilization']:
        print_info("Note: Stabilization requires two-pass processing and will take longer")
        # For simplicity, we'll skip the detect pass in this version
        # You can add vidstabdetect + vidstabtransform if needed
        vfilters.append('vidstabtransform=smoothing=30:zoom=5')
    
    # Resolution
    if choices['resolution']:
        vfilters.append(f"scale={choices['resolution']}:flags=lanczos")
    
    # Frame rate
    if choices['fps']:
        vfilters.append(f"fps={choices['fps']}")
    
    # Apply filters
    if vfilters:
        cmd.extend(['-vf', ','.join(vfilters)])
    
    # Video encoding
    cmd.extend(['-c:v', choices['codec']])
    
    if choices['use_nvenc']:
        # NVENC specific settings
        cmd.extend([
            '-preset', choices['preset'],
            '-b:v', choices['bitrate'],
            '-maxrate', choices['bitrate'],
            '-bufsize', f"{int(choices['bitrate'][:-1]) * 2}M",
            '-rc', 'vbr',
            '-rc-lookahead', '32',
            '-spatial-aq', '1',
            '-temporal-aq', '1',
        ])
        
        if 'hevc' in choices['codec']:
            cmd.extend(['-tier', 'high'])
    else:
        # CPU encoding settings
        cmd.extend([
            '-preset', choices['preset'],
            '-crf', '23',
            '-b:v', choices['bitrate'],
        ])
    
    # Audio encoding
    cmd.extend(['-c:a', 'aac', '-b:a', '192k'])
    
    # Output
    cmd.append(str(output_file))
    
    print_info("FFmpeg command:")
    print(f"{Colors.YELLOW}{' '.join(cmd)}{Colors.END}\n")
    
    # Execute FFmpeg
    try:
        print_info("Encoding in progress... This may take a while.")
        print()
        
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Monitor progress
        for line in process.stdout:
            if 'frame=' in line or 'time=' in line:
                print(f"\r{Colors.CYAN}{line.strip()}{Colors.END}", end='', flush=True)
        
        process.wait()
        print()  # New line after progress
        
        if process.returncode == 0:
            print_success(f"Video merged successfully!")
            print_success(f"Output: {output_file}")
            
            # Show file size
            size_mb = output_file.stat().st_size / (1024 * 1024)
            print_info(f"File size: {size_mb:.2f} MB")
        else:
            print_error("FFmpeg encoding failed!")
            return None
            
    except KeyboardInterrupt:
        print_error("\nEncoding interrupted by user!")
        process.kill()
        return None
    except Exception as e:
        print_error(f"Error during encoding: {e}")
        return None
    finally:
        # Cleanup concat file
        if concat_file.exists():
            concat_file.unlink()
    
    return output_file


def main():
    """Main function"""
    print_header("GoPro Video Merger with NVENC")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Get input directory
    if len(sys.argv) > 1:
        input_dir = Path(sys.argv[1])
    else:
        input_path = input(f"{Colors.CYAN}Enter input directory (default: current): {Colors.END}").strip()
        input_dir = Path(input_path) if input_path else Path.cwd()
    
    if not input_dir.exists() or not input_dir.is_dir():
        print_error(f"Directory not found: {input_dir}")
        sys.exit(1)
    
    # Find and sort videos
    video_files = find_gopro_videos(input_dir)
    
    if not video_files:
        print_error("No video files found!")
        sys.exit(1)
    
    print_success(f"Found {len(video_files)} video files")
    
    # Show chronological order
    print(f"\n{Colors.BOLD}Chronological order:{Colors.END}")
    for i, video in enumerate(video_files, 1):
        duration_str = format_duration(video['duration'])
        print(f"  {i:2d}. {video['filepath'].name:30s} | "
              f"{video['creation_time'].strftime('%Y-%m-%d %H:%M:%S')} | "
              f"{duration_str}")
    
    print()
    confirm = input(f"{Colors.CYAN}Proceed with merge? [Y/n]: {Colors.END}").strip().lower()
    if confirm and confirm != 'y':
        print_info("Cancelled by user")
        sys.exit(0)
    
    # Get encoding options
    choices = get_user_choices()
    
    # Set output directory
    output_dir = input_dir / "merged_output"
    
    # Merge videos
    output_file = merge_videos(video_files, output_dir, choices)
    
    if output_file:
        print_header("DONE!")
        print_success("All videos merged successfully!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.END}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)