import os
import shutil
from fastapi import UploadFile

# --- DÜZELTME BURADA ---
# Dosyanın (image_service.py) kendi konumunu buluyoruz
current_file_path = os.path.abspath(__file__) # .../Applora/app/services/image_service.py

# Buradan geriye doğru giderek Ana Proje Klasörünü (Applora) buluyoruz
# 1. dirname -> app/services
# 2. dirname -> app
# 3. dirname -> Applora (Ana Klasör)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(current_file_path)))

# Hedef: Applora/static
STATIC_DIR = os.path.join(BASE_DIR, "static")
# -----------------------

def save_image(file: UploadFile, subfolder: str, filename: str) -> str:
    """
    Dosyayı Applora/static klasörünün içine kaydeder.
    """
    # Kayıt klasörü: .../Applora/static/profile_images
    folder_path = os.path.join(STATIC_DIR, subfolder)
    
    # Klasör yoksa oluştur
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    
    # Dosyanın tam yolu
    file_path = os.path.join(folder_path, filename)
    
    # Dosyayı diske yaz
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Veritabanına kaydedilecek yol (Tarayıcının anlayacağı formatta)
    return f"/static/{subfolder}/{filename}"

def delete_image(db_path: str):
    """
    Veritabanındaki yola sahip dosyayı siler.
    """
    if not db_path:
        return

    # db_path: /static/profile_images/resim.jpg
    # Bunu gerçek dosya yoluna çevirmemiz lazım.
    # Baştaki "/static/" kısmını atıp, kendi STATIC_DIR yolumuzu ekliyoruz.
    
    # "/static/" kısmını temizle -> profile_images/resim.jpg
    relative_path = db_path.lstrip("/static/")
    relative_path = relative_path.lstrip("/") # Garanti olsun diye tekrar temizle
    
    # .../Applora/static/profile_images/resim.jpg
    file_path = os.path.join(STATIC_DIR, relative_path)
    
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Dosya silinemedi: {e}")