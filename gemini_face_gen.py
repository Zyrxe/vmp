import os
import requests
import base64
from dotenv import load_dotenv

# ==========================
# 1️⃣ Konfigurasi API
# ==========================
# Buat file .env di folder yang sama, isi dengan:
# GEMINI_API_KEY=AIzaSy************
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("API Key belum diatur. Tambahkan di file .env")

# ==========================
# 2️⃣ Masukkan gambar wajah
# ==========================
FACE_IMAGE_PATH = "face.jpg"  # Ganti dengan nama file foto kamu
ASPECT_RATIO = "1080x1920"   # Rasio 9:16 (bisa diganti ke 1024x1024 atau 1920x1080)

with open(FACE_IMAGE_PATH, "rb") as f:
    image_base64 = base64.b64encode(f.read()).decode("utf-8")

# ==========================
# 3️⃣ Prompt
# ==========================
prompt_text = (
    f"Analyze the provided male face image. "
    f"Describe it in detailed, realistic visual terms without changing identity. "
    f"Then generate a text prompt for recreating the same face as a {ASPECT_RATIO} portrait, "
    f"keeping facial structure, skin tone, and expression identical. "
    f"Output only the final image prompt description."
)

# ==========================
# 4️⃣ Request ke Gemini API
# ==========================
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

headers = {
    "Content-Type": "application/json",
    "x-goog-api-key": API_KEY
}

payload = {
    "contents": [
        {
            "parts": [
                {"text": prompt_text},
                {
                    "inline_data": {
                        "mime_type": "image/jpeg",
                        "data": image_base64
                    }
                }
            ]
        }
    ]
}

response = requests.post(url, headers=headers, json=payload)

if response.status_code != 200:
    print("❌ Error:", response.status_code, response.text)
    exit()

# ==========================
# 5️⃣ Ambil deskripsi wajah
# ==========================
result = response.json()
try:
    description = result["candidates"][0]["content"]["parts"][0]["text"]
except Exception:
    description = "Gagal membaca respons dari Gemini."

print("\n✅ Deskripsi wajah dari Gemini:")
print(description)

# ==========================
# 6️⃣ (Opsional) Kirim ke OpenAI / Stable Diffusion
# ==========================
# Jika kamu ingin hasil berupa gambar, aktifkan bagian di bawah dan isi API OpenAI kamu.

USE_IMAGE_GENERATOR = False

if USE_IMAGE_GENERATOR:
    print("\n🖼️ Mengirim ke generator gambar...")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    dalle_url = "https://api.openai.com/v1/images/generations"
    dalle_headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    dalle_payload = {
        "model": "gpt-image-1",
        "prompt": description,
        "size": ASPECT_RATIO
    }
    dalle_response = requests.post(dalle_url, headers=dalle_headers, json=dalle_payload)
    print("\n✅ Respons generator gambar:")
    print(dalle_response.json())
