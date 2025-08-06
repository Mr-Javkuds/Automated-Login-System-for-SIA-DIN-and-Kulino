# login_chrome.py
import json
import time
import os
import subprocess
import sys
import threading
import urllib.request
import zipfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# =============== KONFIGURASI UTAMA ===============
CONFIG_FILE = "config.json"
CHROMEDRIVER = "chromedriver.exe"
SIADIN_URL = "https://mhs.dinus.ac.id/"
KULINO_URL = "https://kulino.dinus.ac.id/"

# Konfigurasi untuk chromedriver
CHROMEDRIVER_VERSION = "138.0.7204.183"  # Ganti dengan versi yang kompatibel
CHROMEDRIVER_BASE_URL = f"https://storage.googleapis.com/chrome-for-testing-public/{CHROMEDRIVER_VERSION}/win64/chromedriver-win64.zip"
CHROMEDRIVER_ZIP = "chromedriver-win64.zip"

def check_and_install_selenium():
    """Periksa dan instal modul selenium jika belum ada."""
    try:
        import selenium
        print("✅ Modul 'selenium' sudah terinstal.")
        return True
    except ImportError:
        print("⚠️ Modul 'selenium' tidak ditemukan. Mencoba menginstal...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "selenium"])
            print("✅ Modul 'selenium' berhasil diinstal.")
            return True
        except Exception as e:
            print(f"❌ Gagal menginstal 'selenium': {e}")
            print("💡 Pastikan koneksi internet aktif, atau instal secara manual dengan: pip install selenium")
            return False

def check_and_download_chromedriver():
    """Periksa dan unduh chromedriver.exe jika belum ada."""
    if os.path.exists(CHROMEDRIVER):
        print(f"✅ File '{CHROMEDRIVER}' ditemukan.")
        return True

    print(f"⚠️ File '{CHROMEDRIVER}' tidak ditemukan. Mengunduh dari internet...")
    try:
        print(f"⬇️ Mengunduh {CHROMEDRIVER_BASE_URL}...")
        with urllib.request.urlopen(CHROMEDRIVER_BASE_URL) as response, open(CHROMEDRIVER_ZIP, 'wb') as out_file:
            data = response.read()
            out_file.write(data)
        print("✅ Download selesai.")

        # Verifikasi file
        if not os.path.exists(CHROMEDRIVER_ZIP):
            raise FileNotFoundError(f"File {CHROMEDRIVER_ZIP} tidak ditemukan setelah download.")
        print(f"✅ File {CHROMEDRIVER_ZIP} berhasil dibuat.")

        # Mengekstrak
        print("📦 Mengekstrak file...")
        with zipfile.ZipFile(CHROMEDRIVER_ZIP, 'r') as zip_ref:
            zip_ref.extractall(".")
        print("✅ Ekstraksi selesai.")

        # Pindahkan chromedriver.exe ke direktori utama jika berada dalam folder
        extracted_driver = os.path.join("chromedriver-win64", "chromedriver.exe")
        if os.path.exists(extracted_driver):
            os.replace(extracted_driver, CHROMEDRIVER)
            # Hapus folder yang sekarang kosong
            os.rmdir("chromedriver-win64")

        # Hapus file zip
        os.remove(CHROMEDRIVER_ZIP)
        print(f"✅ File sementara {CHROMEDRIVER_ZIP} dihapus.")
        return True

    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        print(f"❌ URL Error: {e.reason}")
    except Exception as e:
        print(f"❌ Gagal mengunduh {CHROMEDRIVER}: {e}")
        print("💡 Unduh manual dari: https://googlechromelabs.github.io/chrome-for-testing/")
    return False

def load_config():
    """Membaca konfigurasi dari file JSON."""
    if not os.path.exists(CONFIG_FILE):
        print("❌ File konfigurasi 'config.json' tidak ditemukan di USB.")
        print("💡 Pastikan file ini ada di folder yang sama dengan script ini.")
        return None

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            siadin_nim = data.get('siadin', {}).get('nim')
            siadin_password = data.get('siadin', {}).get('password')
            kulino_nim = data.get('kulino', {}).get('nim')
            kulino_password = data.get('kulino', {}).get('password')

            if not siadin_nim or not siadin_password:
                print("❌ NIM atau Password untuk SiAdin kosong di 'config.json'.")
                return None
            if not kulino_nim or not kulino_password:
                print("❌ NIM atau Password untuk Kulino kosong di 'config.json'.")
                return None

            return {
                'siadin': {'nim': siadin_nim, 'password': siadin_password},
                'kulino': {'nim': kulino_nim, 'password': kulino_password}
            }
    except json.JSONDecodeError as e:
        print(f"❌ File 'config.json' rusak atau bukan format JSON yang valid: {e}")
    except Exception as e:
        print(f"❌ Gagal membaca file konfigurasi: {e}")
    return None

def login_to_siadin(driver, wait, credentials):
    """Fungsi untuk login ke SiAdin."""
    print("🌐 Membuka halaman SiAdin...")
    driver.get(SIADIN_URL)

    print("🔐 Menunggu field NIM siap...")
    try:
        nim_field = wait.until(EC.element_to_be_clickable((By.ID, "username")))
        nim_field.clear()
        nim_field.send_keys(credentials['siadin']['nim'])
        print("✅ NIM berhasil diisi.")
    except TimeoutException:
        print("❌ Timeout: Field NIM tidak ditemukan.")
        raise

    print("🔐 Menunggu field Password siap...")
    try:
        password_field = wait.until(EC.element_to_be_clickable((By.ID, "password")))
        password_field.clear()
        password_field.send_keys(credentials['siadin']['password'])
        print("✅ Password berhasil diisi.")
    except TimeoutException:
        print("❌ Timeout: Field Password tidak ditemukan.")
        raise

    print("🖱️ Menunggu tombol 'Masuk ke SiAdin' bisa diklik...")
    try:
        login_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Masuk ke SiAdin")]')))
        login_button.click()
        print("✅ Klik tombol login SiAdin berhasil!")
    except TimeoutException:
        print("❌ Timeout: Tombol login SiAdin tidak bisa diklik.")
        raise

def login_to_kulino(driver, wait, credentials):
    """Fungsi untuk login ke Kulino."""
    print("🌐 Membuka halaman Kulino...")
    # Buka tab baru dan arahkan ke Kulino
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(KULINO_URL)

    # Tunggu sebentar untuk melihat apakah sudah otomatis masuk
    time.sleep(3)

    # Cek apakah kita sudah di halaman utama (sudah login)
    try:
        # Cari form login
        login_form = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "form.navbar-form")))
        print("ℹ️ Ditemukan form login. Melanjutkan proses login ke Kulino...")

        # Ekstrak nilai logintoken
        try:
            logintoken_input = driver.find_element(By.NAME, "logintoken")
            logintoken_value = logintoken_input.get_attribute("value")
            print(f"🔑 Token keamanan ditemukan: {logintoken_value}")
        except Exception as e:
            print(f"❌ Gagal mengekstrak logintoken: {e}")
            raise

        # Isi NIM dan Password
        print("🔐 Mengisi NIM di Kulino...")
        username_input = driver.find_element(By.NAME, "username")
        username_input.clear()
        username_input.send_keys(credentials['kulino']['nim'])

        print("🔐 Mengisi Password di Kulino...")
        password_input = driver.find_element(By.NAME, "password")
        password_input.clear()
        password_input.send_keys(credentials['kulino']['password'])

        # Klik tombol login
        print("🖱️ Mengklik tombol login Kulino...")
        submit_button = driver.find_element(By.ID, "submit")
        submit_button.click()
        print("✅ Login ke Kulino berhasil!")

    except TimeoutException:
        # Jika form login tidak ditemukan dalam waktu tertentu, kita anggap sudah login
        print("✅ Sudah masuk ke Kulino secara otomatis (SSO).")
    except Exception as e:
        print(f"❌ Gagal login ke Kulino: {e}")
        raise

def monitor_usb_drive(driver, usb_drive):
    """
    Fungsi untuk memantau keberadaan drive USB.
    Jika drive tidak ditemukan, tutup browser.
    """
    print(f"🔍 Memulai pemantauan drive USB: {usb_drive}")
    while True:
        if not os.path.exists(usb_drive):
            print(f"\n🚨 USB telah dicabut! Menutup browser...")
            try:
                driver.quit()  # Ini akan menutup browser dan chromedriver
                print("✅ Browser berhasil ditutup.")
            except Exception as e:
                print(f"❌ Gagal menutup browser: {e}")
            break  # Hentikan loop pemantauan
        time.sleep(2)  # Periksa setiap 2 detik

def main():
    print("🚀 Memulai proses login ke SiAdin dan Kulino...")

    # Dapatkan drive letter dari mana script ini dijalankan
    usb_drive = f"{os.path.splitdrive(os.path.abspath(__file__))[0]}\\"
    print(f"💿 USB drive terdeteksi: {usb_drive}")

    # ======== LANGKAH 1: PERIKSA DEPENDENSI ========
    print("\n🔍 Memeriksa dependensi...")
    if not check_and_install_selenium():
        input("\nTekan Enter untuk keluar...")
        return

    if not check_and_download_chromedriver():
        input("\nTekan Enter untuk keluar...")
        return

    # ======== LANGKAH 2: BACA KONFIGURASI ========
    config = load_config()
    if not config:
        input("\nTekan Enter untuk keluar...")
        return

    # ======== LANGKAH 3: LOGIN KE SISTEM ========
    options = ChromeOptions()
    # options.add_argument("--headless")  # Aktifkan untuk mode tak terlihat
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    service = ChromeService(CHROMEDRIVER)

    driver = None
    try:
        print("🔧 Memulai Chrome...")
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 20)

        # =============== LOGIN KE SIADIN ===============
        login_to_siadin(driver, wait, config)

        # =============== LOGIN KE KULINO ===============
        login_to_kulino(driver, wait, config)

        # =============== SELESAI ===============
        print("\n🎉 Login ke SiAdin dan Kulino berhasil!")
        print("ℹ️ Browser akan tetap terbuka. Anda bisa beralih antar tab.")
        print("🛑 Jika USB dicabut, browser akan ditutup secara otomatis.")
        print("🔚 Proses otomasi ini akan berhenti sekarang.")

        # ⭐⭐⭐ MULAI THREAD PEMANTAUAN USB ⭐⭐⭐
        monitor_thread = threading.Thread(target=monitor_usb_drive, args=(driver, usb_drive), daemon=True)
        monitor_thread.start()

        # Biarkan script utama tetap berjalan
        while monitor_thread.is_alive():
            time.sleep(1)

    except TimeoutException as e:
        print(f"\n❌ Proses login gagal karena timeout: {e}")
        print("Pastikan koneksi internet stabil dan halaman dapat diakses.")
    except WebDriverException as e:
        print(f"\n❌ Terjadi kesalahan WebDriver: {e}")
    except Exception as e:
        print(f"\n❌ Terjadi kesalahan yang tidak terduga: {e}")
    finally:
        # Hanya panggil driver.quit() jika terjadi error DAN driver berhasil dibuat
        if driver is not None:
            print("🔄 Menutup browser karena terjadi kesalahan...")
            driver.quit()

if __name__ == "__main__":
    main()