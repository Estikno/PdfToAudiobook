from pydub import AudioSegment
from pathlib import Path
import subprocess
import os

# 📁 Carpeta con los bloques
TEMP_FOLDER = "temp"
OUTPUT_MP3 = "audiobook.mp3"
LIST_FILE = "file_list.txt"

def join_wavs_to_mp3(temp_folder, output_file):
    audio_files = sorted(Path(temp_folder).glob("block_*.wav"), key=lambda x: int(x.stem.split("_")[1]))
    
    if not audio_files:
        print("No wav files have been found in the temp folder.")
        return
    
    with open(LIST_FILE, "w", encoding="utf-8") as f:
        for wav in audio_files:
            f.write(f"file '{wav.as_posix()}'\n")

    # Excecute Fmmpeg to concatenate the wavs
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", LIST_FILE,
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        output_file
    ]
    subprocess.run(cmd, check=True)
    print(f"Audiobook created successfully: {output_file}")

if __name__ == "__main__":
    join_wavs_to_mp3(TEMP_FOLDER, OUTPUT_MP3)
