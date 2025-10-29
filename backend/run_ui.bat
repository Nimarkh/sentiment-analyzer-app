@echo off
echo Starting Streamlit UI...
cd /d %~dp0
..\venv\Scripts\streamlit run ui_app.py
pause

