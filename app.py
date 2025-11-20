from sanic import Sanic
from sanic.response import json
import hashlib, secrets, smtplib, os
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from dotenv import load_dotenv
from sanic_cors import CORS
import asyncio
from functools import partial

# Ortam değişkenlerini yükle (.env)
load_dotenv()

app = Sanic("CampusHubAPI")
CORS(app)

# Basit kullanıcı "veritabanı"
USERS = {
    "ali@gmail.com": {
        "name": "Ali Yılmaz",
        "password": hashlib.sha256("12345".encode()).hexdigest()
    }
}

# Şifre sıfırlama token deposu
RESET_TOKENS = {}

# ---------------- Yardımcı Fonksiyon ----------------
def send_email_sync(email, reset_link):
    msg = EmailMessage()
    msg["Subject"] = "CampusHub Ankara - Şifre Sıfırlama"
    msg["From"] = os.getenv("GMAIL_USER")
    msg["To"] = email
    msg.set_content(
        f"Merhaba,\n\nŞifreni sıfırlamak için: {reset_link}\n\nCampusHub Ekibi"
    )

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.getenv("GMAIL_USER"), os.getenv("GMAIL_PASS"))
        smtp.send_message(msg)

# ---------------- Ana Sayfa ----------------
@app.get("/")
async def home(request):
    return json({"mesaj": "CampusHub Ankara API çalışıyor 🚀"})

# ---------------- Kayıt Ol ----------------
@app.post("/api/kayit-ol")
async def kayit_ol(request):
    data = request.json
    email = data.get("email", "").strip().lower()
    name = data.get("name", "").strip()
    password = data.get("password", "")

    if not email or not password or not name:
        return json({"basarili": False, "mesaj": "Tüm alanları doldurmanız gerekiyor."}, status=400)

    if email in USERS:
        return json({"basarili": False, "mesaj": "Bu e-posta zaten kayıtlı."}, status=409)

    if len(password) < 6:
        return json({"basarili": False, "mesaj": "Şifre en az 6 karakter olmalıdır."}, status=400)

    USERS[email] = {
        "name": name,
        "password": hashlib.sha256(password.encode()).hexdigest()
    }

    return json({"basarili": True, "mesaj": "Hesabınız başarıyla oluşturuldu!"}, status=201)

# ---------------- Giriş ----------------
@app.post("/api/giris")
async def giris(request):
    data = request.json
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = USERS.get(email)
    if not user:
        return json({"basarili": False, "mesaj": "Bu e-posta ile kayıt bulunamadı."}, status=404)

    hashed = hashlib.sha256(password.encode()).hexdigest()
    if user["password"] == hashed:
        return json({"basarili": True, "mesaj": f"Hoş geldin, {user['name']}!"}, status=200)
    else:
        return json({"basarili": False, "mesaj": "Şifre yanlış."}, status=401)

# ---------------- Şifremi Unuttum ----------------
@app.post("/api/sifremi-unuttum")
async def sifremi_unuttum(request):
    data = request.json
    email = data.get("email", "").strip().lower()

    if email not in USERS:
        return json({"basarili": False, "mesaj": "Bu e-posta sistemde kayıtlı değil."}, status=404)

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
    RESET_TOKENS[token] = {"email": email, "expires_at": expires_at}

    reset_link = f"http://localhost:5173/sifre-sifirla?token={token}"

    try:
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, partial(send_email_sync, email, reset_link))
        
        return json({"basarili": True, "mesaj": "Şifre sıfırlama bağlantısı gönderildi."})
    except Exception as e:
        print("Mail gönderim hatası:", e)
        return json({"basarili": False, "mesaj": "E-posta gönderilirken hata oluştu."}, status=500)

# ---------------- Şifre Sıfırla ----------------
@app.post("/api/sifre-sifirla")
async def sifre_sifirla(request):
    data = request.json
    token = data.get("token", "")
    new_password = data.get("password", "")

    entry = RESET_TOKENS.get(token)
    now_utc = datetime.now(timezone.utc)

    if not entry or entry["expires_at"] < now_utc:
        return json({"basarili": False, "mesaj": "Bağlantı geçersiz veya süresi dolmuş."}, status=400)

    if len(new_password) < 6:
        return json({"basarili": False, "mesaj": "Şifre en az 6 karakter olmalıdır."}, status=400)

    email = entry["email"]
    USERS[email]["password"] = hashlib.sha256(new_password.encode()).hexdigest()
    del RESET_TOKENS[token]

    return json({"basarili": True, "mesaj": "Şifreniz başarıyla sıfırlandı."}, status=200)

# ---------------- Çalıştır ----------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
