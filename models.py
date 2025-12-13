from tortoise import fields, models

# 1. Kullanıcı Tablosu (Giriş/Kayıt için en önemlisi bu)
class User(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=255, unique=True)
    password = fields.CharField(max_length=255)
    name = fields.CharField(max_length=255, null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "users"

# 2. Kullanıcı Profili (Detaylar için)
class UserProfile(models.Model):
    id = fields.IntField(pk=True)
    user = fields.OneToOneField("models.User", related_name="profile")
    bio = fields.TextField(null=True)
    avatar = fields.CharField(max_length=255, null=True)
    
    class Meta:
        table = "user_profiles"

# 3. Etkinlikler Tablosu
class Event(models.Model):
    id = fields.IntField(pk=True)
    title = fields.CharField(max_length=255)
    description = fields.TextField()
    date = fields.DatetimeField()
    location = fields.CharField(max_length=255)
    
    class Meta:
        table = "events"

# 4. Favori Etkinlikler
class FavouriteEvent(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="favorites")
    event = fields.ForeignKeyField("models.Event", related_name="favorited_by")
    
    class Meta:
        table = "favourite_events"

# 5. Geri Bildirimler
class Feedback(models.Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField("models.User", related_name="feedbacks")
    message = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "feedbacks"

# 6. İletişim Kullanıcı Tipleri (Öğrenci, Personel vb.)
class ContactUserTypes(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)

    class Meta:
        table = "contact_user_types"

# 7. İletişim Konu Tipleri (Şikayet, Öneri vb.)
class ContactTopicTypes(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100)

    class Meta:
        table = "contact_topic_types"

# 8. İletişim Mesajları
class ContactMessages(models.Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    email = fields.CharField(max_length=255)
    message = fields.TextField()
    # İlişkiler (Opsiyonel olarak null olabilir)
    user_type = fields.ForeignKeyField("models.ContactUserTypes", null=True)
    topic_type = fields.ForeignKeyField("models.ContactTopicTypes", null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "contact_messages"
