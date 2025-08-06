import subprocess
import sys
import os

def is_selenium_installed():
    try:
        import selenium
        return True
    except ImportError:
        return False

def install_from_whl(whl_path):
    print(f"📦 Menginstal selenium dari: {whl_path}")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", whl_path])
        print("✅ Selenium berhasil diinstal dari file .whl.")
    except subprocess.CalledProcessError as e:
        print("❌ Gagal menginstal selenium dari file .whl.")
        print(f"Error: {e}")
        sys.exit(1)

def main():
    if is_selenium_installed():
        print("✅ Selenium sudah terinstal.")
        return

    current_dir = os.path.dirname(os.path.abspath(__file__))
    whl_file = os.path.join(current_dir, "selenium-4.34.2-py3-none-any.whl")

    if not os.path.exists(whl_file):
        print(f"❌ File .whl tidak ditemukan: {whl_file}")
        sys.exit(1)

    install_from_whl(whl_file)

if __name__ == "__main__":
    main()
    input("\n🔚 Tekan Enter untuk keluar...")
