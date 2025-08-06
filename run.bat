@echo off
:: run.bat - Jalankan login SiAdin dari USB sebagai Administrator
:: Versi: 1.3
:: Penulis: Assistant AI

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

:: Jalankan file VBS dan hapus setelah selesai
cscript /nologo "%vbs_script%"
del "%vbs_script%" 2>nul
exit /b

:run_script
:: Jika sudah berjalan sebagai admin, lanjutkan

echo 🚀 Menyiapkan proses login SiAdin...

:: Ubah direktori kerja ke lokasi script
cd /d "%~dp0"

:: Cek Python
where python >nul 2>&1
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    where python3 >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=python3
    ) else (
        echo ❌ Python tidak ditemukan. Pastikan Python terinstal.
        echo 💡 Buka https://www.python.org/downloads/ untuk menginstal Python.
        pause
        exit /b 1
    )
)

:: Jalankan script
echo 🔧 Menjalankan login_firefox.py...
call %PYTHON_CMD% "login_firefox.py"

:: Tampilkan hasil
if %errorlevel% equ 0 (
    echo ✅ Script selesai berhasil.
) else (
    echo ❌ Script selesai dengan error (kode: %errorlevel%).
)

pause