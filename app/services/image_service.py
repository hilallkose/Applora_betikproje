import os
import shutil
from fastapi import UploadFile

# Resimlerin kaydedileceği ana klasör yolu
STATIC_DIR = "app/static"

def save_image(file: UploadFile, subfolder: str, filename: str) -> str:
    """
    Dosyayı belirtilen klasöre kaydeder ve veritabanı için yolunu döndürür.
    """
    # Kayıt klasörü: app/static/images veya app/static/profile_images
    folder_path = os.path.join(STATIC_DIR, subfolder)
    
    # Klasör yoksa oluştur
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Dosyanın tam yolu
    file_path = os.path.join(folder_path, filename)
    
    # Dosyayı diske yaz
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Veritabanına kaydedilecek yol (örn: /static/images/resim.jpg)
    # "app/static" kısmını "/static" olarak değiştiriyoruz ki tarayıcı bulabilsin
    return f"/static/{subfolder}/{filename}"

def delete_image(db_path: str):
    """
    Veritabanındaki yola (örn: /static/images/x.jpg) sahip dosyayı siler.
    """
    if not db_path:
        return

    # /static/images/x.jpg -> app/static/images/x.jpg yoluna çeviriyoruz
    # db_path.lstrip("/") baştaki / işaretini kaldırır
    file_path = os.path.join("app", db_path.lstrip("/"))
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Dosya silinemedi: {e}")