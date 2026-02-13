import os
import uuid
import shutil
import math
import tempfile
from typing import Dict, Any, List
from config.supabase import supabase_client
from app.tools.file_handler import FileHandler
from app.tools.media_converter import MediaConverter
from app.tools.cost_calculator import CostCalculator
from app.schemas.HrSchemas import InterviewAnalysisOutput
from core.BaseAgent import BaseAgent
from app.llm.factory import get_groq
from pydub import AudioSegment
import logging

logger = logging.getLogger(__name__)

# Prompt Template for Interview Analysis
PROMPT_TEMPLATE = """
# Role and Goal
Anda adalah seorang Senior Talent Acquisition Specialist dan Interview Analyst profesional. 
Tugas utama Anda adalah melakukan analisis mendalam terhadap transkrip wawancara kerja untuk mengevaluasi kompetensi, gaya komunikasi, dan kecocokan kandidat terhadap peran yang dilamar.

# Context
Berikut adalah transkrip hasil rekaman wawancara antara rekruter dan kandidat:
---
{transcript}
---

# Rules
1. **Berbasis Bukti (Evidence-Based):** Setiap poin dalam kelebihan dan kekurangan harus didasarkan pada pernyataan atau perilaku yang teramati dalam transkrip. Jangan berasumsi.
2. **Bahasa Profesional:** Gunakan Bahasa Indonesia yang formal, objektif, dan konstruktif (sesuai EYD).
3. **Analisis Komunikasi:** Evaluasi bukan hanya *apa* yang dikatakan, tetapi *bagaimana* kandidat menyampaikannya (kejelasan, struktur berpikir, dan relevansi).
4. **Kepatuhan Skema JSON:** Output harus berupa JSON murni yang valid sesuai skema. Jangan sertakan teks pembuka atau penutup di luar blok JSON.
5. **Objektivitas:** Berikan penilaian yang jujur. Jika ada keraguan atau jawaban yang kontradiktif, catat hal tersebut di bagian kekurangan atau kesimpulan.

# Workflow Steps
1. **Scanning Transkrip:** Baca seluruh transkrip untuk memahami alur percakapan dan konteks pertanyaan yang diajukan.
2. **Evaluasi Alur:** Analisis apakah proses wawancara berlangsung dua arah, apakah kandidat dominan, atau apakah ada hambatan komunikasi yang signifikan.
3. **Identifikasi Kompetensi:** Ekstrak poin-poin kunci mengenai hard skill, soft skill, dan pengalaman relevan yang dipaparkan kandidat.
4. **Penilaian Kualitas:** Nilai kualitas jawaban berdasarkan parameter STAR (Situation, Task, Action, Result) jika memungkinkan, serta tingkat kepercayaan diri kandidat.
5. **Sintesis Final:**
    - Susun ringkasan proses yang padat.
    - Rincikan kelebihan dan kekurangan secara spesifik (dalam bentuk list).
    - Berikan kesimpulan akhir yang memberikan rekomendasi nyata (misal: lanjut ke tahap user, perlu tes teknis tambahan, atau tidak disarankan).
"""

class InterviewService(BaseAgent):
    
    def __init__(self, llm, **kwargs):
        super().__init__(
            llm=llm,
            prompt_template=PROMPT_TEMPLATE,
            output_model=InterviewAnalysisOutput,
            use_structured_output=True,
            **kwargs
        )
        self.groq_client = get_groq()

    async def __call__(self, user_id: str, file_path: str) -> Dict[str, Any]:
        # Create cross-platform temp directory
        temp_base = tempfile.gettempdir()
        temp_dir = os.path.join(temp_base, f"interview_{uuid.uuid4()}")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Define paths using os.path.join for cross-platform compatibility
        original_filename = os.path.basename(file_path)
        local_original_path = os.path.join(temp_dir, original_filename)
        local_audio_path = os.path.join(temp_dir, "processed_audio.flac")
        
        try:
            # 1. Download File from Supabase
            logger.info(f"Downloading file from Supabase: {file_path}")
            try:
                # Use FileHandler or direct Supabase client. 
                # Since FileHandler is static, let's use supabase client directly for stream download 
                # or just use the storage.download method which returns bytes.
                data = supabase_client.storage.from_("hr-files").download(file_path)
                with open(local_original_path, "wb") as f:
                    f.write(data)
            except Exception as e:
                raise ValueError(f"Failed to download file '{file_path}': {str(e)}")

            # 2. Validation: Max 250MB check (Backend safety net)
            file_size_mb = os.path.getsize(local_original_path) / (1024 * 1024)
            if file_size_mb > 250:
                # Clean up immediately if too large
                raise ValueError(f"File too large ({file_size_mb:.2f}MB). Max limit is 250MB.")

            # 3. Convert/Compress to Audio
            logger.info("Converting/Compressing media...")
            MediaConverter.compress_audio(local_original_path, local_audio_path)
            
            # 4. DELETE ORIGINAL from Supabase to save space
            logger.info(f"Deleting original file from Supabase: {file_path}")
            supabase_client.storage.from_("hr-files").remove([file_path])
            
            # 5. Upload Processed Audio to Supabase
            # Create a new path for the processed audio
            processed_filename = f"processed_audio/{uuid.uuid4()}.flac"
            logger.info(f"Uploading processed audio to Supabase: {processed_filename}")
            
            with open(local_audio_path, "rb") as f:
                supabase_client.storage.from_("hr-files").upload(
                    path=processed_filename,
                    file=f,
                    file_options={"content-type": "audio/flac"}
                )

            # 6. Check processed size & Transcribe (using local processed file)
            processed_size_mb = os.path.getsize(local_audio_path) / (1024 * 1024)
            full_transcript = ""
            
            logger.info("Starting transcription...")
            if processed_size_mb <= 25:
                # Direct Transcription
                full_transcript = self._transcribe_file(local_audio_path)
            else:
                # Chunking (Splitting into 10 min segments)
                logger.info(f"File size {processed_size_mb:.2f}MB > 25MB. Chunking...")
                full_transcript = self._transcribe_chunks(local_audio_path, temp_dir)

            # 7. Analyze with LLM
            logger.info("Analyzing transcript with LLM...")
            self.rebind_prompt_variable(transcript=full_transcript)
            raw_output, parsed_output = await self.arun_chain(input="Analyze Interview")
            result = parsed_output.model_dump()

            # 8. Log Activity
            try:
                log_data = {
                    "user_id": user_id,
                    "tool_type": "interview_analyzer",
                    "input_files": [processed_filename], # Reference the new processed file
                    "result_json": result,
                    "cost_usd": 0.0, # Placeholder
                    "token_usage": {"audio_size_mb": processed_size_mb}
                }
                supabase_client.table("activity_logs").insert(log_data).execute()
            except Exception as e:
                logger.error(f"Logging failed: {str(e)}")

            return result

        finally:
            # Cleanup local temp files
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)

    def _transcribe_file(self, file_path: str) -> str:
        with open(file_path, "rb") as f:
            transcription = self.groq_client.audio.transcriptions.create(
                file=(os.path.basename(file_path), f.read()),
                model="whisper-large-v3-turbo",
                language="id",
                prompt="Transkrip wawancara kerja antara rekruter dan kandidat. Gunakan Ejaan Yang Disempurnakan (EYD).",
                response_format="text"
            )
        return transcription

    def _transcribe_chunks(self, file_path: str, temp_dir: str) -> str:
        audio = AudioSegment.from_file(file_path)
        # 10 minutes = 600,000 ms
        chunk_length_ms = 10 * 60 * 1000 
        chunks = [audio[i:i + chunk_length_ms] for i in range(0, len(audio), chunk_length_ms)]
        
        transcript_parts = []
        for i, chunk in enumerate(chunks):
            chunk_path = os.path.join(temp_dir, f"chunk_{i}.flac")
            chunk.export(chunk_path, format="flac")
            
            # Double check chunk size (rarely > 25MB for 10mins flac mono 16khz, but good safety)
            if os.path.getsize(chunk_path) / (1024*1024) > 25:
                logger.warning(f"Chunk {i} is still > 25MB! Consider shorter chunks.")
            
            part_text = self._transcribe_file(chunk_path)
            transcript_parts.append(part_text)
            
        return " ".join(transcript_parts)
