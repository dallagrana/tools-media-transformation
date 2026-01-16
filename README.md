# GoPro Video Merger with NVENC

A powerful Python script to automatically merge GoPro footage in chronological order using NVIDIA GPU hardware acceleration (NVENC) for fast, high-quality video encoding.

## 🎯 Purpose

GoPro cameras split long recordings into multiple files (typically 4GB chunks). This script:
- **Automatically detects** all GoPro video files in a directory
- **Sorts them chronologically** using file metadata timestamps
- **Merges them seamlessly** into a single video file
- **Leverages your NVIDIA GPU** (RTX 3090) for fast hardware encoding
- **Provides interactive options** for output format, resolution, and quality

## ✨ Features

### Automatic Processing
- 📁 Scans directory for all MP4 video files
- ⏰ Extracts creation timestamps from video metadata
- 🔄 Sorts videos chronologically (even if filenames are out of order)
- 📊 Shows detailed information before merging

### Hardware Acceleration
- 🚀 **NVENC support** - Uses your RTX 3090 for ultra-fast encoding
- ⚡ **10-20x faster** than CPU encoding
- 🎮 Doesn't impact gaming/other GPU tasks significantly
- 💪 Supports multiple NVIDIA codecs (H.264, H.265, AV1)

### Flexible Output Options

**Encoding Method:**
- NVIDIA NVENC (Hardware - Recommended)
- CPU Software encoding (Fallback)

**Video Codecs:**
- H.264 (h264_nvenc) - Best compatibility, works everywhere
- H.265/HEVC (hevc_nvenc) - 30-50% better compression
- AV1 (av1_nvenc) - Newest standard, best quality/size ratio

**Resolution:**
- 4K (3840x2160)
- 2K (2560x1440)
- 1080p (1920x1080)
- 720p (1280x720)
- Keep original

**Frame Rate:**
- 60 fps
- 30 fps
- Keep original

**Additional:**
- Video stabilization (vidstab filter)
- Quality presets (p1/p4/p7 for NVENC)
- Custom bitrate control

## 📋 Prerequisites

### Required Software
- **Python 3.6+**
- **FFmpeg** with NVENC support
- **FFprobe** (comes with FFmpeg)
- **NVIDIA GPU** with NVENC support (GTX 600 series or newer)

### Install FFmpeg with NVENC

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Check NVENC support:**
```bash
ffmpeg -encoders | grep nvenc
```

You should see output like:
```
 V....D h264_nvenc           NVIDIA NVENC H.264 encoder
 V....D hevc_nvenc           NVIDIA NVENC hevc encoder
 V....D av1_nvenc            NVIDIA NVENC AV1 encoder
```

## 🚀 Installation

1. **Download the script:**
```bash
wget https://raw.githubusercontent.com/YOUR_REPO/gopro_merge.py
# or copy the script manually
```

2. **Make it executable:**
```bash
chmod +x gopro_merge.py
```

3. **Verify dependencies:**
```bash
python3 gopro_merge.py
```
The script will check if FFmpeg and FFprobe are installed correctly.

## 📖 Usage

### Basic Usage

Navigate to your GoPro footage directory and run:
```bash
cd /path/to/gopro/videos
python3 /path/to/gopro_merge.py
```

Or specify the directory as an argument:
```bash
python3 gopro_merge.py /path/to/gopro/videos
```

### Interactive Workflow

The script will guide you through the process:

1. **Scan and Sort**
   ```
   Scanning directory: /path/to/videos
     Found: GH011595.MP4 - 2023-10-12 10:27:43
     Found: GH021595.MP4 - 2023-10-12 11:00:15
     ...
   ✓ Found 15 video files
   ```

2. **Review Chronological Order**
   ```
   Chronological order:
     1. GH011595.MP4 | 2023-10-12 10:27:43 | 00:11:23
     2. GH021595.MP4 | 2023-10-12 11:00:15 | 00:11:23
     ...
   ```

3. **Confirm Merge**
   ```
   Proceed with merge? [Y/n]:
   ```

4. **Choose Encoding Options**
   ```
   Encoding method:
     1. NVIDIA NVENC (Hardware - Recommended)
     2. CPU (Software - Slower)
   Select [1-2] (default: 1):
   ```

5. **Select Output Settings**
   - Choose codec (H.264/H.265/AV1)
   - Select resolution
   - Set frame rate
   - Enable/disable stabilization
   - Choose quality preset
   - Set bitrate

6. **Watch Progress**
   ```
   Encoding in progress... This may take a while.
   frame=12450 fps=387 q=28.0 size=  512000kB time=00:03:27.50 bitrate=20234.5kbits/s speed=12.9x
   ```

7. **Done!**
   ```
   ✓ Video merged successfully!
   ✓ Output: gopro_merged_20231012_h264_20260116_073000.mp4
   ℹ File size: 2847.32 MB
   ```

### Output Location

Merged videos are saved to:
```
/path/to/gopro/videos/merged_output/
```

Output filename format:
```
gopro_merged_[DATE]_[CODEC]_[TIMESTAMP].mp4
```

Example: `gopro_merged_20231012_h264_20260116_073000.mp4`

## 🎬 Example Scenarios

### Scenario 1: Quick Merge (Keep Original Settings)
Your GoPro files: 15 clips, 4K 60fps, ~40GB total

**Settings:**
- NVENC H.264
- Keep original resolution (4K)
- Keep original fps (60)
- No stabilization
- Bitrate: 50 Mbps

**Result:** 
- Processing time: ~5-10 minutes on RTX 3090
- Output size: ~35GB
- Quality: Virtually identical to original

### Scenario 2: Compressed for Sharing
**Settings:**
- NVENC H.265
- 1080p resolution
- 30 fps
- Bitrate: 20 Mbps

**Result:**
- Processing time: ~8-12 minutes
- Output size: ~8-10GB
- Quality: Excellent for YouTube/sharing

### Scenario 3: Maximum Quality Archive
**Settings:**
- NVENC H.265
- 4K original
- 60 fps original
- Preset: p7 (slowest, best quality)
- Bitrate: 80 Mbps

**Result:**
- Processing time: ~15-20 minutes
- Output size: ~30GB
- Quality: Reference quality

## ⚙️ Performance

### NVENC vs CPU Encoding

**NVENC (RTX 3090):**
- ⚡ Speed: ~300-500 fps on 4K60 content
- ⏱️ Real-time factor: 10-15x
- 🔋 GPU usage: 30-50%
- 💻 CPU usage: <10%

**CPU (Software):**
- 🐌 Speed: ~20-40 fps on 4K60 content
- ⏱️ Real-time factor: 0.3-0.7x
- 💻 CPU usage: 100%
- ⏰ 10-20x slower than NVENC

### Recommended Settings by Use Case

| Use Case | Codec | Resolution | FPS | Bitrate | Result |
|----------|-------|------------|-----|---------|--------|
| **Archive/Keep Original** | H.265 | 4K | 60 | 60-80M | Best quality |
| **YouTube Upload** | H.264 | 4K | 60 | 40-50M | Excellent |
| **Social Media** | H.264 | 1080p | 30 | 15-20M | Great |
| **Quick Preview** | H.264 | 720p | 30 | 8-10M | Good |
| **Maximum Compression** | H.265 | 1080p | 30 | 10-15M | Small file |

## 🔧 Advanced Options

### Custom Bitrate
When prompted for bitrate, enter your desired Mbps:
```
Enter bitrate in Mbps (default: 50): 80
```

Higher bitrate = better quality but larger file size

### Stabilization
Video stabilization uses the `vidstab` filter:
- Smooths out camera shake
- Adds processing time (~20-30% slower)
- May introduce slight crop
- Best for handheld/action footage

## 🐛 Troubleshooting

### FFmpeg Not Found
```bash
# Install FFmpeg
sudo apt install ffmpeg

# Verify installation
ffmpeg -version
```

### NVENC Not Available
```bash
# Check NVENC support
ffmpeg -encoders | grep nvenc

# Install NVIDIA drivers
sudo apt install nvidia-driver-XXX

# Verify GPU
nvidia-smi
```

### "No video files found"
- Ensure you're in the correct directory
- Check file extensions (script looks for .mp4 and .MP4)
- Verify files are readable

### Encoding Fails
- Check available disk space in output directory
- Verify all input files are valid video files
- Check FFmpeg error messages for specific issues

### Slow Encoding
- Ensure NVENC is selected (not CPU)
- Check GPU isn't being used by other applications
- Try a faster preset (p1 instead of p7)
- Monitor GPU usage with `nvidia-smi`

## 📊 Understanding GoPro File Naming

GoPro cameras use this naming convention:
```
GH[CHAPTER][CLIP].MP4
```

**Examples:**
- `GH011595.MP4` - Clip 1595, Chapter 01
- `GH021595.MP4` - Clip 1595, Chapter 02 (continuation)
- `GH031595.MP4` - Clip 1595, Chapter 03 (continuation)

**Why chapters?**
- GoPro splits files at ~4GB due to FAT32 limits
- Chapters are sequential parts of the same recording
- This script automatically handles chapters and sorts correctly

## 🤝 Tips & Best Practices

1. **Always backup** original footage before processing
2. **Free up disk space** - merged file can be large
3. **Use NVENC** for speed - quality is excellent with your RTX 3090
4. **Start with defaults** - they work well for most cases
5. **Test settings** on a few clips before processing large batches
6. **Monitor GPU** with `nvidia-smi` during encoding
7. **Keep originals** until you verify the merged output

## 📝 Technical Details

### How It Works

1. **Scanning Phase:**
   - Scans directory for .MP4 files
   - Uses FFprobe to extract video metadata
   - Reads creation timestamps from video file tags
   - Falls back to file modification time if needed

2. **Sorting Phase:**
   - Sorts all videos by creation timestamp
   - Displays chronological order for user verification
   - Handles GoPro's chapter system automatically

3. **Concatenation Phase:**
   - Creates FFmpeg concat demuxer file
   - Lists all input videos in order
   - Ensures safe file path handling

4. **Encoding Phase:**
   - Builds FFmpeg command with selected options
   - Applies video filters (scale, fps, stabilization)
   - Uses NVENC hardware encoder
   - Encodes audio to AAC
   - Shows real-time progress

5. **Cleanup Phase:**
   - Removes temporary concat file
   - Reports final file size and location

### FFmpeg Command Example

For NVENC H.264 at 4K 60fps:
```bash
ffmpeg -y \
  -f concat -safe 0 -i concat_list.txt \
  -c:v h264_nvenc \
  -preset p4 \
  -b:v 50M \
  -maxrate 50M \
  -bufsize 100M \
  -rc vbr \
  -rc-lookahead 32 \
  -spatial-aq 1 \
  -temporal-aq 1 \
  -c:a aac -b:a 192k \
  output.mp4
```

## 📄 License

This script is provided as-is for personal use. Feel free to modify and adapt to your needs.

## 🙏 Credits

- Uses FFmpeg for video processing
- NVENC developed by NVIDIA
- Designed for GoPro action cameras

## 📮 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify FFmpeg and NVENC are working correctly
3. Review FFmpeg error messages for specific problems

---

**Happy merging! 🎥✨**

*Optimized for NVIDIA RTX 3090 and GoPro footage*
