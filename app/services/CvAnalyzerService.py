import json
import base64
from config.supabase import supabase_client
# Removed PdfExtractor
from app.tools.cost_calculator import CostCalculator
from app.schemas.HrSchemas import CvAnalysisOutput
from core.BaseAgent import BaseAgent
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage

prompt_template = """
# Role and Goal
Anda adalah seorang Ahli Perekrutan HR dan Spesialis Akuisisi Bakat berpengalaman dalam perekrutan teknis maupun non-teknis. 
Tujuan utama Anda adalah melakukan analisis Curriculum Vitae (CV) kandidat secara mendalam, objektif, dan berbasis data terhadap Deskripsi Pekerjaan dan Kriteria yang ditentukan.

# Context
- **Judul Pekerjaan:** {job_title}
- **Target Kriteria:** {job_criteria}

# Rules
1. **Prioritaskan Objektivitas:** Dasarkan evaluasi Anda sepenuhnya pada bukti yang ditemukan dalam CV yang diberikan. Jangan berasumsi tentang keahlian atau pengalaman yang tidak dinyatakan secara eksplisit atau tersirat dengan kuat.
2. **Kepatuhan Skema & Bahasa:** Anda harus memberikan output dalam format JSON yang sesuai dengan skema. **Semua konten teks (seperti strengths, weaknesses, dan summary) WAJIB ditulis dalam Bahasa Indonesia yang profesional dan formal.** Jangan sertakan teks pembuka atau penutup di luar JSON.
3. **Logika Penilaian:** 
    - 0-40: Kecocokan buruk, tidak memenuhi persyaratan inti.
    - 41-70: Kecocokan parsial, memiliki beberapa keterampilan relevan tetapi kurang pengalaman kunci.
    - 71-90: Kecocokan kuat, memenuhi sebagian besar kriteria dan memiliki latar belakang yang relevan.
    - 91-100: Kecocokan luar biasa, melampaui kriteria yang diminta.
4. **Wawasan yang Dapat Ditindaklanjuti:** Kekuatan (strengths) dan kelemahan (weaknesses) harus spesifik dan terkait langsung dengan Kriteria Pekerjaan.
5. **Hindari Halusinasi:** Jika dokumen tidak terbaca, korup, atau tidak relevan, atur `match_analysis` ke false dan jelaskan alasannya dengan jujur di bagian `summary`.

# Workflow Steps
1. **Analisis Persyaratan:** Pahami Judul Pekerjaan dan Kriteria untuk menentukan profil "Kandidat Ideal".
2. **Pemindaian Dokumen:** Tinjau dokumen CV (gambar/PDF) yang disediakan untuk mengekstrak riwayat kerja, keterampilan, pendidikan, dan sertifikasi.
3. **Analisis Kesenjangan (Gap Analysis):** Bandingkan data yang diekstrak dengan Target Kriteria. Identifikasi poin-poin di mana kandidat unggul dan di mana mereka kekurangan.
4. **Sintesis Temuan:** 
    - Tentukan status kecocokan (`match_analysis`: True/False).
    - Susun daftar kekuatan utama dan kelemahan kritis.
    - Berikan skor numerik akhir (0-100).
5. **Peninjauan Akhir:** Pastikan bagian `summary` memberikan justifikasi profesional atas skor dan status kecocokan dalam Bahasa Indonesia yang baik dan benar (EYD).
"""

class CvAnalyzerService(BaseAgent):
    
    def __init__(self, llm, **kwargs):
        super().__init__(
            llm=llm,
            prompt_template=prompt_template,
            output_model=CvAnalysisOutput,
            use_structured_output=True,
            **kwargs
        )
    
    async def __call__(self, user_id: str, job_id: int, file_path: str, file_bytes: bytes) -> Dict[str, Any]:
        # 1. Fetch Job Criteria
        job_res = supabase_client.table("job_positions").select("criteria_text, title").eq("id", job_id).single().execute()
        if not job_res.data:
            raise ValueError("Job position not found")
        job_criteria = job_res.data["criteria_text"]
        job_title = job_res.data["title"]

        # 2. Prepare Multimodal Input (Base64)
        # Convert bytes to base64 string
        base64_pdf = base64.b64encode(file_bytes).decode('utf-8')

        # Construct Multimodal Message
        # This matches the structure LangChain expects for "blob" or "file" content
        # Note: For LangChain Google GenAI specifically, we often use `image_url` structure or raw content blocks.
        # But per the generic Multimodal docs, we can try the dictionary format.
        
        multimodal_input = [
            {
                "type": "text", 
                "text": "Please analyze this CV document based on the job criteria provided in the system prompt."
            },
            {
                "type": "media", # or "image_url" for some providers, but "media" / "blob" for generic files if supported
                # For Gemini specifically, standard usage often involves passing the blob with mime_type
                "file_uri": None,
                "mime_type": "application/pdf",
                "data": base64_pdf
            }
        ]
        
        # Alternatively, using the format you referenced (LangChain generic message content):
        message_content = [
            {"type": "text", "text": "Analyze this CV document."},
            {
                "type": "image_url", # LangChain often maps "image_url" to generic media inputs for Gemini
                "image_url": {"url": f"data:application/pdf;base64,{base64_pdf}"} 
            }
        ]
        
        # 3. Rebind Variables (Job context is still in system/prompt template)
        self.rebind_prompt_variable(
            job_title=job_title,
            job_criteria=job_criteria
        )
        
        # 4. Run Chain
        # Pass the multimodal content as the 'input'. 
        # BaseAgent wraps 'input' in a HumanMessage.
        raw_output, parsed_output = await self.arun_chain(input=message_content)

        print(raw_output)
        
        # 5. Calculate Cost & Log (Simplified)
        # ... (Log logic remains similar) ...
        
        # ... existing logging code ...
        log_data = {
            "user_id": user_id,
            "tool_type": "cv_analyzer",
            "input_files": [file_path],
            "output_files": [],
            "result_json": parsed_output.model_dump(),
            "cost_usd": 0, # Difficult to calc tokens for PDF binary without API response metadata
            "token_usage": {}
        }
        supabase_client.table("activity_logs").insert(log_data).execute()
        
        return parsed_output.model_dump()
