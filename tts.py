from TTS.api import TTS
import json
from pydub import AudioSegment
import os
import re
import torch

INPUT_JSON = "classified_text.json"
# Temporary folder to store the intermidiate wavs
TEMP_FOLDER = "temp"

# Function that splits a text into chunks, if they are too long (250 chars by default in English) TTS won't work properly
def split_text(text, max_length=250):
    # We remove extra spaces
    text = re.sub(r"\s+", " ", text.strip())

    chunks = []

    # We first divide the text into sentences
    sentences = re.split(r'(?<=[\.\?\!;])\s+', text)

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        # If the sentence is not too long, we add it to the chunks
        if len(sentence) <= max_length:
            chunks.append(sentence)
            continue

        # If the sentence is too long, we split it into smaller parts
        subparts = re.split(r'(?<=,)\s+', sentence)
        temp = ""
        for part in subparts:
            if len(temp) + len(part) + 1 <= max_length:
                temp += (" " + part if temp else part)
            else:
                if temp:
                    chunks.append(temp.strip())
                temp = part
        if temp:
            chunks.append(temp.strip())

    # If it's still too long then we split it into smaller chunks, even if it's mid sentence, but never dividing a word
    final_chunks = []
    for chunk in chunks:
        if len(chunk) <= max_length:
            final_chunks.append(chunk)
        else:
            words = chunk.split(" ")
            temp = ""
            for word in words:
                if len(temp) + len(word) + 1 <= max_length:
                    temp += (" " + word if temp else word)
                else:
                    if temp:
                        final_chunks.append(temp.strip())
                    temp = word
            if temp:
                final_chunks.append(temp.strip())

    return final_chunks

def generate_audiobook_coqui(input_json):
    os.makedirs(TEMP_FOLDER, exist_ok=True)

    # Load your chosen TTS model
    tts = TTS(model_name="tts_models/multilingual/multi-dataset/xtts_v2", progress_bar=True)

    # If you have a GPU that supports CUDA, I recommend using it. 
    if torch.cuda.is_available():
        tts.to("cuda")

    with open(input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    for i, block in enumerate(data, start=1):
        # Skip blocks that you already have the audio
        # if i <= 644:
        #     continue

        print(f"Processing block {i}/{len(data)}...")

        label = block.get("label", "body")
        text = block["text"].strip()
        
        # By default it ignores blocks with the "other" label
        if not text or label == "other":
            continue

        # Pause durations in milliseconds
        pause_duration = 1000 if label == "header" else 500 if label == "caption" else 200

        # Split block text into chunks of max 250 chars
        text_chunks = split_text(text, max_length=250)

        # Combine all chunks audio for this block
        block_audio = AudioSegment.silent(duration=0)

        for j, chunk in enumerate(text_chunks):
            temp_wav = os.path.join(TEMP_FOLDER, f"block_{i}_chunk_{j}.wav")
            print(f" Synthesizing block {i} chunk {j} ({len(chunk)} chars)")
            
            # Additional settings for the TTS model, modify the language and the speaker
            tts.tts_to_file(text=chunk, file_path=temp_wav, speaker="Adde Michal", language="en")

            segment = AudioSegment.from_wav(temp_wav)
            if j < len(text_chunks) - 1:
                # Short pause between chunks
                block_audio += segment + AudioSegment.silent(duration=50)
            else:
                # Last chunk of the block --> apply longer pause
                block_audio += segment + AudioSegment.silent(duration=pause_duration)

            os.remove(temp_wav)

        block_wav_path = os.path.join(TEMP_FOLDER, f"block_{i}.wav")
        block_audio.export(block_wav_path, format="wav")
        print(f" Saved combined block audio: {block_wav_path}")

    # Export combined audiobook to MP3
    print(f"✅ Audiobook segments saved in /temp folder")

if __name__ == "__main__":
    generate_audiobook_coqui(INPUT_JSON)
