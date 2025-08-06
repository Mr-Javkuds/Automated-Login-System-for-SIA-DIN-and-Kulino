# tests/test_login_functions.py
import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
import os
import threading
import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# Tambahkan direktori utama ke path agar bisa mengimpor login_firefox
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Impor fungsi dari script utama
from login_firefox import (
    load_config,
    check_and_install_selenium,
    check_and_download_geckodriver,
    login_to_siadin,
    login_to_kulino,
    monitor_usb_drive,
    main
)

# Impor kelas yang dibutuhkan untuk mocking
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import WebDriverException

class TestLoginFunctions(unittest.TestCase):

    # --- TEST load_config() ---
    @patch('builtins.open', new_callable=mock_open, read_data='{"siadin": {"nim": "1234567890", "password": "pass123"}, "kulino": {"nim": "0987654321", "password": "pass456"}}')
    @patch('os.path.exists')
    def test_load_config_success(self, mock_exists, mock_open):
        """Test: load_config berhasil membaca file konfigurasi."""
        mock_exists.return_value = True
        config = load_config()
        self.assertIsNotNone(config)
        self.assertEqual(config['siadin']['nim'], '1234567890')
        self.assertEqual(config['kulino']['password'], 'pass456')

    @patch('os.path.exists')
    def test_load_config_file_not_found(self, mock_exists):
        """Test: load_config mengembalikan None jika file tidak ditemukan."""
        mock_exists.return_value = False
        with patch('builtins.print') as mock_print:
            config = load_config()
            self.assertIsNone(config)
            mock_print.assert_any_call("❌ File konfigurasi 'config.json' tidak ditemukan di USB.")

    @patch('os.path.exists')
    def test_load_config_invalid_json(self, mock_exists):
        """Test: load_config mengembalikan None jika file JSON rusak."""
        mock_exists.return_value = True
        with patch('builtins.open', mock_open(read_data='{invalid json')) as mock_file:
            with patch('builtins.print') as mock_print:
                config = load_config()
                self.assertIsNone(config)
                # Perbaiki string yang dicocokkan
                mock_print.assert_any_call("❌ File 'config.json' rusak atau bukan format JSON yang valid:")

    # --- TEST check_and_install_selenium() ---
    @patch('subprocess.check_call')
    @patch('builtins.__import__')
    def test_check_and_install_selenium_already_installed(self, mock_import, mock_check_call):
        """Test: check_and_install_selenium berhasil jika selenium sudah terinstal."""
        mock_import.return_value = MagicMock()
        result = check_and_install_selenium()
        self.assertTrue(result)
        mock_check_call.assert_not_called()

    @patch('subprocess.check_call')
    @patch('builtins.__import__')
    def test_check_and_install_selenium_install_success(self, mock_import, mock_check_call):
        """Test: check_and_install_selenium berhasil menginstal selenium."""
        mock_import.side_effect = ImportError
        mock_check_call.return_value = 0
        result = check_and_install_selenium()
        self.assertTrue(result)
        mock_check_call.assert_called_once()

    @patch('subprocess.check_call', side_effect=Exception("Installation failed"))
    @patch('builtins.__import__', side_effect=ImportError)
    def test_check_and_install_selenium_install_failure(self, mock_import, mock_check_call):
        """Test: check_and_install_selenium gagal menginstal selenium."""
        with patch('builtins.print') as mock_print:
            result = check_and_install_selenium()
            self.assertFalse(result)
            mock_print.assert_any_call("❌ Gagal menginstal 'selenium': Installation failed")

    # --- TEST check_and_download_geckodriver() ---
    @patch('os.path.exists')
    def test_check_and_download_geckodriver_already_exists(self, mock_exists):
        """Test: check_and_download_geckodriver tidak mengunduh jika file sudah ada."""
        mock_exists.return_value = True
        with patch('urllib.request.urlretrieve') as mock_urlretrieve:
            result = check_and_download_geckodriver()
            self.assertTrue(result)
            mock_urlretrieve.assert_not_called()

    @patch('os.path.exists')
    @patch('urllib.request.urlretrieve')
    @patch('zipfile.ZipFile')
    @patch('os.remove')
    def test_check_and_download_geckodriver_download_success(self, mock_remove, mock_zip, mock_urlretrieve, mock_exists):
        """Test: check_and_download_geckodriver berhasil mengunduh dan mengekstrak."""
        mock_exists.side_effect = [False, True]  # Pertama kali tidak ada, setelah download ada
        mock_urlretrieve.return_value = None
        mock_zip_instance = mock_zip.return_value.__enter__.return_value
        mock_zip_instance.extractall.return_value = None
        mock_remove.return_value = None

        result = check_and_download_geckodriver()
        self.assertTrue(result)
        mock_urlretrieve.assert_called_once()
        mock_zip.assert_called_once()
        mock_remove.assert_called_once()

    @patch('os.path.exists')
    @patch('urllib.request.urlretrieve', side_effect=Exception("Download failed"))
    def test_check_and_download_geckodriver_download_failure(self, mock_urlretrieve, mock_exists):
        """Test: check_and_download_geckodriver gagal mengunduh."""
        mock_exists.return_value = False
        with patch('builtins.print') as mock_print:
            result = check_and_download_geckodriver()
            self.assertFalse(result)
            # Perbaiki string yang dicocokkan
            mock_print.assert_any_call("❌ Gagal mengunduh geckodriver: Download failed")

    # --- TEST login_to_siadin() ---
    @patch.object(webdriver, 'Firefox')
    def test_login_to_siadin_success(self, mock_driver_class):
        """Test: login_to_siadin berhasil."""
        mock_driver = mock_driver_class.return_value
        mock_wait = MagicMock(spec=WebDriverWait)
        mock_wait.until = MagicMock(side_effect=lambda x: x)

        # Buat mock untuk elemen dengan metode clear() dan send_keys()
        mock_nim_field = MagicMock()
        mock_password_field = MagicMock()
        mock_login_button = MagicMock()

        # Simulasikan pencarian elemen
        mock_driver.find_element.side_effect = [
            mock_nim_field,
            mock_password_field,
            mock_login_button
        ]

        credentials = {'siadin': {'nim': '1234567890', 'password': 'pass123'}}

        # Jalankan fungsi
        login_to_siadin(mock_driver, mock_wait, credentials)

        # Verifikasi interaksi
        mock_driver.get.assert_called_with("https://mhs.dinus.ac.id/")
        mock_nim_field.send_keys.assert_called_with('1234567890')
        mock_password_field.send_keys.assert_called_with('pass123')
        mock_login_button.click.assert_called_once()

    # --- TEST login_to_kulino() ---
    @patch.object(webdriver, 'Firefox')
    def test_login_to_kulino_success(self, mock_driver_class):
        """Test: login_to_kulino berhasil."""
        mock_driver = mock_driver_class.return_value
        mock_wait = MagicMock(spec=WebDriverWait)
        mock_wait.until = MagicMock(side_effect=lambda x: x)

        # Buat mock untuk elemen
        mock_logintoken_input = MagicMock()
        mock_logintoken_input.get_attribute.return_value = "dummy_token"
        mock_username_input = MagicMock()
        mock_password_input = MagicMock()
        mock_submit_button = MagicMock()

        # Simulasikan pencarian elemen
        mock_driver.find_element.side_effect = [
            mock_logintoken_input,    # logintoken
            mock_username_input,      # username
            mock_password_input,      # password
            mock_submit_button        # submit
        ]

        credentials = {'kulino': {'nim': '0987654321', 'password': 'pass456'}}

        # Jalankan fungsi
        login_to_kulino(mock_driver, mock_wait, credentials)

        # Verifikasi interaksi
        mock_driver.execute_script.assert_called_with("window.open('');")
        mock_driver.switch_to.window.assert_called_with(mock_driver.window_handles[-1])
        mock_driver.get.assert_called_with("https://kulino.dinus.ac.id/")
        mock_username_input.send_keys.assert_called_with('0987654321')
        mock_password_input.send_keys.assert_called_with('pass456')
        mock_submit_button.click.assert_called_once()

    # --- TEST monitor_usb_drive() ---
    @patch('os.path.exists')
    def test_monitor_usb_drive_usb_removed(self, mock_exists):
        """Test: monitor_usb_drive menutup driver jika USB dicabut."""
        mock_driver = MagicMock()
        mock_exists.side_effect = [True, False]  # Awalnya ada, lalu dicabut

        # Jalankan fungsi dalam thread terpisah
        monitor_thread = threading.Thread(target=monitor_usb_drive, args=(mock_driver, "D:\\"), daemon=True)
        monitor_thread.start()
        time.sleep(0.1)  # Beri waktu untuk thread berjalan

        # Verifikasi bahwa driver.quit() dipanggil
        mock_driver.quit.assert_called_once()

    @patch('os.path.exists')
    def test_monitor_usb_drive_usb_still_plugged(self, mock_exists):
        """Test: monitor_usb_drive tidak menutup driver jika USB masih terpasang."""
        mock_driver = MagicMock()
        mock_exists.return_value = True  # USB tetap terpasang

        # Jalankan fungsi dalam thread terpisah
        monitor_thread = threading.Thread(target=monitor_usb_drive, args=(mock_driver, "D:\\"), daemon=True)
        monitor_thread.start()
        time.sleep(0.1)  # Beri waktu untuk thread berjalan

        # Hentikan thread secara manual
        monitor_thread.join(timeout=0.1)

        # Verifikasi bahwa driver.quit() TIDAK dipanggil
        mock_driver.quit.assert_not_called()

    # --- TEST main() ---
    @patch('login_firefox.load_config')
    @patch('login_firefox.check_and_install_selenium')
    @patch('login_firefox.check_and_download_geckodriver')
    @patch('login_firefox.login_to_siadin')
    @patch('login_firefox.login_to_kulino')
    @patch('login_firefox.monitor_usb_drive')
    @patch.object(webdriver, 'Firefox')
    @patch('os.path.splitdrive')
    @patch('os.path.abspath')
    def test_main_success(self, mock_abspath, mock_splitdrive, mock_firefox, mock_monitor, mock_login_kulino, mock_login_siadin, mock_download, mock_install, mock_load_config):
        """Test: main() berhasil menjalankan seluruh alur tanpa error."""
        # Konfigurasi mock
        mock_abspath.return_value = "D:\\SiAdin_Login_Firefox\\login_firefox.py"
        mock_splitdrive.return_value = ("D:", "\\SiAdin_Login_Firefox\\login_firefox.py")
        mock_load_config.return_value = {
            'siadin': {'nim': '1234567890', 'password': 'pass123'},
            'kulino': {'nim': '0987654321', 'password': 'pass456'}
        }
        mock_install.return_value = True
        mock_download.return_value = True
        mock_firefox.return_value = MagicMock()

        # Jalankan fungsi main()
        # Karena main() memiliki loop infinite, kita perlu menghentikannya
        with patch('time.sleep', side_effect=KeyboardInterrupt):
            try:
                main()
            except SystemExit:
                pass  # Ini normal karena KeyboardInterrupt

        # Verifikasi bahwa fungsi-fungsi penting dipanggil
        mock_load_config.assert_called_once()
        mock_install.assert_called_once()
        mock_download.assert_called_once()
        mock_login_siadin.assert_called_once()
        mock_login_kulino.assert_called_once()
        mock_monitor.assert_called_once()

    @patch('login_firefox.load_config', return_value=None)
    def test_main_load_config_failure(self, mock_load_config):
        """Test: main() keluar jika load_config gagal."""
        with patch('builtins.input') as mock_input:
            main()
            mock_input.assert_called_once()

    @patch('login_firefox.load_config')
    @patch('login_firefox.check_and_install_selenium', return_value=False)
    def test_main_selenium_install_failure(self, mock_install, mock_load_config):
        """Test: main() keluar jika instalasi selenium gagal."""
        mock_load_config.return_value = {'siadin': {'nim': '1234567890', 'password': 'pass123'}, 'kulino': {'nim': '0987654321', 'password': 'pass456'}}
        with patch('builtins.input') as mock_input:
            main()
            mock_input.assert_called_once()

    @patch('login_firefox.load_config')
    @patch('login_firefox.check_and_install_selenium', return_value=True)
    @patch('login_firefox.check_and_download_geckodriver', return_value=False)
    def test_main_geckodriver_download_failure(self, mock_download, mock_install, mock_load_config):
        """Test: main() keluar jika download geckodriver gagal."""
        mock_load_config.return_value = {'siadin': {'nim': '1234567890', 'password': 'pass123'}, 'kulino': {'nim': '0987654321', 'password': 'pass456'}}
        with patch('builtins.input') as mock_input:
            main()
            mock_input.assert_called_once()

    @patch('login_firefox.load_config')
    @patch('login_firefox.check_and_install_selenium', return_value=True)
    @patch('login_firefox.check_and_download_geckodriver', return_value=True)
    @patch.object(webdriver, 'Firefox')
    def test_main_webdriver_exception(self, mock_firefox, mock_download, mock_install, mock_load_config):
        """Test: main() menangani WebDriverException."""
        mock_load_config.return_value = {'siadin': {'nim': '1234567890', 'password': 'pass123'}, 'kulino': {'nim': '0987654321', 'password': 'pass456'}}
        mock_firefox.side_effect = WebDriverException("WebDriver error")
        with patch('builtins.print') as mock_print:
            main()
            mock_print.assert_any_call("❌ Terjadi kesalahan WebDriver: WebDriver error")

if __name__ == '__main__':
    unittest.main()