import json
import time
import google.generativeai as genai
from django.conf import settings

def generate_batch_recommendations(batch_data: list) -> dict:
    """
    Menerima list berisi maksimal 5 data siswa.
    Mengembalikan dict dengan format { "nisn": {"guru": "...", "orangtua": "...", "siswa": "..."} }
    """
    GEMINI_KEY = getattr(settings, 'GEMINI_API_KEY', None)
    
    # 1. Siapkan Fallback Default (Jika API Error / Limit habis)
    fallback_result = {}
    for student in batch_data:
        fallback_result[student['nisn']] = {
            "guru": "Server AI sedang penuh. Pantau perkembangan nilai siswa ini secara manual.",
            "orangtua": "Mohon perhatikan waktu belajar anak Anda di rumah minggu ini.",
            "siswa": "Tingkatkan intensitas belajarmu dan jangan ragu bertanya pada guru."
        }

    if not GEMINI_KEY:
        print("CRITICAL ERROR: GEMINI_API_KEY tidak terbaca oleh sistem.")
        return fallback_result
        
    genai.configure(api_key=GEMINI_KEY)

    # 2. Arsitektur Prompting Batch (Banyak siswa sekaligus)
    prompt = f"""
    Anda adalah konsultan akademik profesional. Analisis data {len(batch_data)} siswa berikut secara sekaligus:
    {json.dumps(batch_data, indent=2)}

    Tugas: Berikan rekomendasi praktis, suportif, dan sangat spesifik berdasarkan nilai dan mapel masing-masing siswa.
    Anda WAJIB merespons HANYA dalam format JSON Array. Jangan tambahkan teks apa pun di luar JSON Array.
    Struktur WAJIB persis seperti ini:
    [
      {{
        "nisn": "ISI_NISN_SISWA",
        "guru": "Rekomendasi untuk guru...",
        "orangtua": "Saran untuk orang tua...",
        "siswa": "Tindakan untuk siswa..."
      }}
    ]
    """

    model = genai.GenerativeModel("gemini-3.5-flash-lite")
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            response = model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                )
            )
            
            # 3. Parsing JSON Array dari AI
            response_data = json.loads(response.text)
            
            # 4. Mapping hasil AI kembali ke NISN (Mencegah salah alamat / Mismatch)
            final_result = {}
            for item in response_data:
                nisn = item.get("nisn")
                if nisn:
                    final_result[nisn] = {
                        "guru": item.get("guru", fallback_result[nisn]["guru"]),
                        "orangtua": item.get("orangtua", fallback_result[nisn]["orangtua"]),
                        "siswa": item.get("siswa", fallback_result[nisn]["siswa"])
                    }
            
            # Gabungkan dengan fallback jika ada siswa yang terlewat oleh AI
            for nisn in fallback_result:
                if nisn not in final_result:
                    final_result[nisn] = fallback_result[nisn]
                    
            return final_result

        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "429" in error_msg or "exhausted" in error_msg:
                if attempt < max_retries - 1:
                    print(f"⚠️ Limit API. Batch Tertunda. Menunggu 10 detik (Percobaan {attempt + 1}/{max_retries})...")
                    time.sleep(10)
                    continue
            
            print(f"❌ GenAI Batch Error: {e}")
            return fallback_result
            
    return fallback_result