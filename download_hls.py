import yt_dlp
import subprocess
import sys

m3u8_url = "https://vwyn3lxe5fv5.cdn-centaurus.com/hls2/01/13319/1u0oua6aovcx_o/master.m3u8?t=1-7sqNU6Lok98FCG0vSQ5uXiaJg34MYhQIwIC3LX3nw&s=1766541169&e=129600&f=66595289&srv=l7eb38rrr27u4&i=0.4&sp=500&p1=l7eb38rrr27u4&p2=l7eb38rrr27u4&asn=4760"

ydl_opts = {
    'format': 'best[ext=mp4]/best',
    'outtmpl': 'video.%(ext)s',
    'merge_output_format': 'mp4',  # Force proper MP4 container
}

try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([m3u8_url])
    print("✅ Complete! Check video.mp4")

    # Auto-remux if ffmpeg available (fixes warning)
    if subprocess.run(['ffmpeg', '-version'], capture_output=True).returncode == 0:
        print("🔧 Auto-fixing container with ffmpeg...")
        subprocess.run(['ffmpeg', '-i', 'video.mp4', '-c', 'copy', '-map', '0', 'video_fixed.mp4', '-y'])
        print("✅ Fixed version: video_fixed.mp4")

except Exception as e:
    print(f"❌ Error: {e}")
