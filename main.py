from sanic import Sanic
from sanic.response import json
from sanic.exceptions import NotFound
import sqlite3
from datetime import datetime

app = Sanic("Campushub06")

def get_db():
    conn = sqlite3.connect("faqs.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer   TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
    """)
    conn.commit()

    cur.execute("SELECT COUNT(*) AS c FROM faqs;")
    if cur.fetchone()["c"] == 0:
        now = datetime.utcnow().isoformat()
        seed = [
            ("Bu sitede hangi üniversitelerin etkinliklerini görebilirim?",
             "Bilkent,TOBB ETÜ,Atılım,Başkent,ODTÜ,Hacettepe,Türk Hava Kurumu"),
            ("Bu site resmi bir üniversite sitesi midir?",
             "Hayır. Bu platform bağımsız bir öğrenci projesidir ve üniversitelerle resmi bir bağlantısı yoktur."),
            ("Sisteme öğrenci olarak üye olmam zorunlu mu?",
             "Hayır, bazı etkinlikler için kayıt gerekir."),
            ("Etkinlik bilgileri nereden alınıyor?",
             "Etkinlikler üniversitelerin resmi internet siteleri, öğrenci kulüpleri ve kurumların halka açık duyurularından alınmaktadır."),
            ("Etkinlikler ücretsiz mi?",
             "Birçok etkinlik ücretsizdir. Ücretli olan etkinliklerde fiyat bilgisi açıkça belirtilir."),
            ("Mobil uygulamanız var mı?",
             "Henüz mobil uygulamamız yok ancak platform tamamen mobil uyumludur."),
            ("Etkinliklerin güncelliği nasıl sağlanıyor?",
             "Sistemimiz üniversite duyuru sayfalarını belirli aralıklarla kontrol eder."),
        ]
        cur.executemany("INSERT INTO faqs (question, answer, created_at) VALUES (?, ?, ?)",
                        [(q, a, now) for q, a in seed])
        conn.commit()
    conn.close()

@app.listener("before_server_start")
async def start(app, loop):
    init_db()

def row_to_dict(r):
    return {
        "id": r["id"],
        "question": r["question"],
        "answer": r["answer"],
        "created_at": r["created_at"],
    }

@app.get("/api/faqs")
async def list_faqs(request):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM faqs ORDER BY id ASC;")
    rows = cur.fetchall()
    conn.close()
    return json([row_to_dict(r) for r in rows])

@app.get("/api/faqs/<faq_id:int>")
async def get_faq(request, faq_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM faqs WHERE id=?", (faq_id,))
    row = cur.fetchone()
    conn.close()

    if not row:
        raise NotFound("FAQ bulunamadı")
    return json(row_to_dict(row))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
