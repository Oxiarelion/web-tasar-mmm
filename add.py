from sanic import Sanic
from sanic.response import text, json

# Uygulamanın ana Sanic objesini 
app = Sanic("campushub_contact")

# İletişim formundan gelen mesajları basitçe tutmak için
CONTACT_MESSAGES = []

USER_TYPES = ["Öğrenci", "Akademisyen", "Kulüp Temsilcisi", "Mezun"]
TOPIC_TYPES = ["Etkinlik ekleme", "Hata bildirimi", "Öneri", "Genel soru"]


@app.get("/")
async def index(request):
    return text("CampusHub Ankara backend çalışıyor! 🎓")


# İletişim sayfasının en üstündeki başlık ve açıklama metnini
@app.get("/contact/header")
async def contact_header(request):
    return json({
        "title": "Bizimle İletişime Geç",
        "subtitle": (
            "CampusHub Ankara bağımsız bir öğrenci platformudur. "
            "Etkinlik ekleme, öneri ve geri bildirim için "
            "bu sayfadan bizimle iletişime geçebilirsin."
        )
    })


# E-posta / GitHub Deposu 
@app.get("/contact/cards")
async def contact_cards(request):
    return json({
        "cards": [
            {
                "type": "email",
                "title": "E-posta",
                "text": "campushub@ankara.edu.tr",
                "href": "mailto:campushub@ankara.edu.tr",
            },
            {
                "type": "github",
                "title": "GitHub Deposu",
                "text": "Açık kaynak kodumuzu görüntüleyin ve katkı verin.",
                "href": "https://github.com/campushub-ankara",
            },
        
        ]
    })


# “Kulüp / Topluluk Musunuz?” kutusunun 
@app.get("/contact/club-info")
async def contact_club_info(request):
    return json({
        "title": "Kulüp / Topluluk Musunuz?",
        "text": (
            "Etkinliklerinizi CampusHub Ankara'da listelemek için "
            "formdan bizimle iletişime geçebilir, kulübünüzü "
            "platforma ekletmek için başvurabilirsiniz."
        )
    })



# “Biz Kimiz?” kısmı
@app.get("/contact/about")
async def contact_about(request):
    return json({
        "title": "Biz Kimiz?",
        "text": (
            "CampusHub Ankara, Ankara’daki üniversite ve kulüp etkinliklerini "
            "tek bir platformda toplayan, öğrenciler tarafından geliştirilen "
            "bağımsız bir öğrenci girişimidir. Amacımız, sosyal medyayı aktif "
            "kullanmayan öğrencilerin de kampüsteki fırsatlara kolayca "
            "ulaşmasını sağlamaktır."
        )
    })


# CampusHub ekibini kartlar halinde gösterebilmek için ekip üyeleri
@app.get("/contact/team")
async def contact_team(request):
    return json({
        "title": "CampusHub Ekibi",
        "members": [
            {
                "name": "İlayda Ceylan",
                "roles": ["Backend", "CI/CD"],
                "photo": None,
            },
            {
                "name": "Zeynep Bahar Arık",
                "roles": ["Frontend", "Data Layer", "Testing"],
                "photo": None,
            },
            {
                "name": "Zeynepnaz Yüksel",
                "roles": ["Backend", "Frontend", "Testing"],
                "photo": None,
            },
            {
                "name": "Buğra Kılıç",
                "roles": ["Backend", "CI/CD"],
                "photo": None,
            },
            {
                "name": "Osman Kapan Mahir",
                "roles": ["Frontend", "Data Layer"],
                "photo": None,
            },
        ]
    })


# Formdaki kullanıcı tipi ve mesaj türü burada
@app.get("/contact/form-options")
async def contact_form_options(request):
    return json({
        "user_types": USER_TYPES,
        "topic_types": TOPIC_TYPES,
    })


# /contact GET isteğini basit bir health-check 
@app.get("/contact")
async def contact_get(request):
    return text("Contact endpoint çalışıyor!")


# İletişim formu gönderildiğinde frontend bu endpoint’e POST isteği atıyor
@app.post("/contact")
async def contact_post(request):
    data = request.json

    # Gövde tamamen boş gelirse erken hata dönüyoru
    if not data:
        return json({"ok": False, "error": "Veri gelmedi."}, status=400)

    # Formda doldurulmasını beklediğim zorunlu alanlar
    required_text_fields = [
        "full_name",   # Ad Soyad
        "email",       # E-posta
        "university",  # Üniversite
        "user_type",   # Kullanıcı tipi 
        "topic",       # Mesaj türü 
        "message",     # Mesaj içeriği
    ]

    # Eksik veya boş bırakılmış alanları tespit ediyor
    missing = [field for field in required_text_fields if not data.get(field)]

    # KVKK kutusunun işaretlenmiş olmalı
    consent = data.get("consent")
    if consent is not True:
        missing.append("consent")

    if missing:
        return json({
            "ok": False,
            "error": "Eksik veya doldurulmamış alanlar var.",
            "missing": missing,
        }, status=400)

    # e posta kontrolü
    if "@" not in data["email"]:
        return json({
            "ok": False,
            "error": "Geçersiz e-posta adresi."
        }, status=400)

    # user_type ve topic alanlarının, tanımladığım listelere uygun olup olmadığını kontrol ediyor
    if data["user_type"] not in USER_TYPES:
        return json({
            "ok": False,
            "error": "Geçersiz kullanıcı tipi.",
        }, status=400)

    if data["topic"] not in TOPIC_TYPES:
        return json({
            "ok": False,
            "error": "Geçersiz mesaj türü.",
        }, status=400)

    # Buradan sonrası, doğrulamayı geçen veriyi kaydetme kısmı
    message_obj = {
        "full_name": data["full_name"],
        "email": data["email"],
        "university": data["university"],
        "user_type": data["user_type"],
        "topic": data["topic"],
        "message": data["message"],
        "consent": True,
    }

    CONTACT_MESSAGES.append(message_obj)
    print("Yeni iletişim mesajı:", message_obj)

    return json({
        "ok": True,
        "message": "İletişim formu başarıyla alındı.",
        "total_messages": len(CONTACT_MESSAGES),
    }, status=201)


# Gelen tüm iletişim mesajlarını basitçe listelendiği endpoint 
@app.get("/contact/messages")
async def list_messages(request):
    return json({
        "ok": True,
        "count": len(CONTACT_MESSAGES),
        "messages": CONTACT_MESSAGES,
    })



# Geliştirme sırasında uygulamayı lokalde bu blok ile ayağa kaldırıyorum
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)
