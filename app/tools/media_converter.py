import ffmpeg
import os
import uuid

class MediaConverter:
    @staticmethod
    def convert_video_to_audio(input_path: str, output_path: str):
        """
        Converts video file to audio file (mp3)
        """
        try:
            stream = ffmpeg.input(input_path)
            stream = ffmpeg.output(stream, output_path)
            ffmpeg.run(stream, overwrite_output=True)
        except ffmpeg.Error as e:
            print(e.stderr.decode())
            raise e

    @staticmethod
    def compress_audio(input_path: str, output_path: str) -> str:
        """
        Compresses audio file to 16kHz mono FLAC to reduce size for Groq/Whisper.
        Command: ffmpeg -i <input> -ar 16000 -ac 1 -map 0:a -c:a flac <output>.flac
        """
        try:
            stream = ffmpeg.input(input_path)
            # -ar 16000: Set audio sampling rate to 16000Hz
            # -ac 1: Set number of audio channels to 1 (mono)
            # -map 0:a: Select audio stream from input 0
            # -c:a flac: Encode audio as FLAC
            stream = ffmpeg.output(stream, output_path, ar=16000, ac=1, map="0:a", **{'c:a': 'flac'})
            ffmpeg.run(stream, overwrite_output=True)
            return output_path
        except ffmpeg.Error as e:
            print(f"FFmpeg Error: {e.stderr.decode() if e.stderr else str(e)}")
            raise RuntimeError(f"Audio compression failed: {str(e)}")

    @staticmethod
    def get_file_size_mb(file_path: str) -> float:
        return os.path.getsize(file_path) / (1024 * 1024)
