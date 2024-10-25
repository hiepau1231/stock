@echo off
cd /d D:\path\to\your\project
call venv\Scripts\activate
python manage.py auto_update_data
