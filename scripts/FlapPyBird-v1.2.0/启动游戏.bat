@echo off
title FlapPy Bird - ��ǿ��
echo ==========================================
echo        FlapPy Bird ��ǿ��
echo ==========================================
echo ����������Ϸ...
echo.

start "" "FlapPyBird.exe"

REM ���EXE�޷����У���ʾ������Ϣ
timeout /t 2 >nul
tasklist /fi "imagename eq FlapPyBird.exe" | find "FlapPyBird.exe" >nul
if %errorlevel% neq 0 (
    echo.
    echo [����] ��Ϸ�����޷���������
    echo.
    echo ���������
    echo 1. �Ҽ�"FlapPyBird.exe" �� �Թ���Ա�������
    echo 2. ȷ��Windows�汾ΪWindows 7�����
    echo 3. ���������⣬����ϵ������
    echo.
    pause
)
