@echo off
:: run.bat - Jalankan login SiAdin dari USB sebagai Administrator
:: Versi: 1.4
:: Penulis: Mr-Javkuds 
:: Periksa apakah script berjalan sebagai administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    goto :run_script
) else (
    goto :request_admin
)

:request_admin
echo.
echo 🚨 Script ini memerlukan hak administrator untuk berjalan.
echo 🔧 Mencoba meminta hak administrator...
echo.

:: Buat file VBS sementara untuk menjalankan UAC prompt
set "vbs_script=%temp%\elevate.vbs"
echo Set UAC = CreateObject^("Shell.Application"^) > "%vbs_script%"
echo UAC.ShellExecute "cmd.exe", "/c ""%~s0""", "", "runas", 1 >> "%vbs_script%"
cscript /nologo "%vbs_script%"
del "%vbs_script%" 2>nul
exit /b

:run_script
echo 🚀 Menyiapkan proses login SiAdin...
cd /d "%~dp0"

:: Deteksi Python
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    where python3 >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
    ) else (
        echo ❌ Python tidak ditemukan. Pastikan Python terinstal.
        echo 💡 https://www.python.org/downloads/
        pause
        exit /b 1
    )
)


:: Cek apakah selenium sudah terinstal
%PYTHON_CMD% -c "import selenium" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Selenium sudah terinstal.
    goto end
)

:: Cek file .whl
if not exist "%~dp0%WHL_FILE%" (
    echo ❌ File %WHL_FILE% tidak ditemukan di folder ini.
    pause
    exit /b 1
)

:: Install selenium dari file .whl
set "WHL_FILE=selenium-4.34.2-py3-none-any.whl"
echo 📦 Menginstal selenium dari file lokal: %WHL_FILE%
%PYTHON_CMD% -m pip install "%WHL_FILE%"
if %errorlevel% neq 0 (
    echo ❌ Gagal menginstal selenium dari file .whl.
    pause
    exit /b 1
) else (
    echo ✅ Selenium berhasil diinstal dari file lokal.
)

:: Jalankan script utama login
echo 🔧 Menjalankan login_firefox.py...
call %PYTHON_CMD% "login_firefox.py"

:: Tampilkan hasil
if %errorlevel% equ 0 (
    echo ✅ Script selesai berhasil.
) else (
    echo ❌ Script selesai dengan error (kode: %errorlevel%).
)

pause
