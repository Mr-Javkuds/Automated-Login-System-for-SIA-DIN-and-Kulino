:: Install selenium dari file .whl
set "WHL_FILE=selenium-4.34.2-py3-none-any.whl"
echo 📦 Menginstal selenium dari file lokal: %WHL_FILE%
%PYTHON_CMD% -m pip install "E:\SiAdin_Login_Firefox\%WHL_FILE%"
if %errorlevel% neq 0 (
    echo ❌ Gagal menginstal selenium dari file .whl.
    pause
    exit /b 1
) else (
    echo ✅ Selenium berhasil diinstal dari file lokal.
)