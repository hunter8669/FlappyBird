@echo off
title FlapPy Bird - ��ǿ����Ϸ
echo ==========================================
echo        FlapPy Bird ��ǿ��
echo ==========================================
echo.
echo ����������Ϸ...
echo.

cd /d "%~dp0"
if exist "FlapPyBird.exe" (
    start "" "FlapPyBird.exe"
    echo ��Ϸ��������
) else (
    echo �����Ҳ��� FlapPyBird.exe
    echo ��ȷ���ļ�����
    pause
)
