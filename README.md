Applora - Sosyal Medya Uygulaması
Applora, Python ve FastAPI kullanılarak geliştirilmiş, modern ve ölçeklenebilir bir sosyal medya platformudur. Kullanıcıların fotoğraf paylaşıp etkileşime girebildiği, birbirini takip edebildiği ve keşfedebildiği "Mini Instagram" tarzı bir yapıdır.

Özellikler:

Bu proje, modern web geliştirme prensipleri ve MVC (Model-View-Controller) benzeri modüler bir yapı kullanılarak geliştirilmiştir.

Güvenli Kimlik Doğrulama: Kayıt Ol, Giriş Yap ve Çıkış Yap (Cookie tabanlı oturum yönetimi & Bcrypt şifreleme).

Medya Paylaşımı: Fotoğraf yükleme, açıklama ekleme ve veritabanına kaydetme.

Profil Yönetimi: Profil fotoğrafı değiştirme, takipçi/takip edilen istatistikleri. 

Etkileşim: Gönderileri beğenme (Like) ve yorum yapma (Comment).

Sosyal Ağ: Kullanıcıları takip etme (Follow) ve takipten çıkma (Unfollow).

Ana Sayfa Akışı (Feed): Tüm kullanıcıların gönderilerini "en yeniden eskiye" doğru akan bir zaman tünelinde görme.

Keşfet & Arama: Kullanıcı adına göre arama yapma ve profilleri ziyaret etme (Ziyaretçi Modu).

Güvenlik Kontrolleri: Başkasının gönderisini silememe, yetkisiz butonları gizleme.

Kullanılan Teknolojiler:

Backend: Python 3.10+, FastAPI

Veritabanı: PostgreSQL, SQLAlchemy (ORM)

Frontend: HTML5, Jinja2 Templates, Bootstrap 5, CSS3

Güvenlik: Passlib (Bcrypt), Python-Multipart

Proje Yapısı

Proje, temiz kod prensiplerine uygun olarak modüler bir şekilde tasarlanmıştır:

Kurulum ve Çalıştırma

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyin:

1. Projeyi Klonlayın
Bash

git clone https://github.com/KULLANICI_ADIN/Applora.git

cd Applora

2. Sanal Ortamı Kurun (Önerilen)

Bash

python -m venv .venv

# Windows için:

.venv\Scripts\activate

# Mac/Linux için:

source .venv/bin/activate

3. Gereksinimleri Yükleyin

Bash

pip install -r requirements.txt

4. Veritabanı Ayarları

PostgreSQL üzerinde bir veritabanı oluşturun. Ardından app/database.py dosyasındaki bağlantı adresini kendi bilgilerinizle güncelleyin:

Python

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:SIFRE@localhost:5432/VERITABANI_ADI"

5. Uygulamayı Başlatın

Bash

uvicorn app.main:app --reload

Tarayıcınızda http://127.0.0.1:8000 adresine giderek uygulamayı kullanmaya başlayabilirsiniz!!!!

Giriş ekranı:

<img width="807" height="799" alt="image" src="https://github.com/user-attachments/assets/e3d98b95-3fa9-42fa-8806-d5c5390f9ae1" />

Profil Sayfası:

<img width="1612" height="864" alt="image" src="https://github.com/user-attachments/assets/bc9b804e-3ce8-4e73-b705-724d73efbb48" />

Ana Akış:

<img width="1225" height="858" alt="image" src="https://github.com/user-attachments/assets/e6f7e963-eb6f-4328-9971-af7d836f3983" />


Geliştirici: Hilal Köse

Bu proje eğitim amaçlı geliştirilmiştir.

