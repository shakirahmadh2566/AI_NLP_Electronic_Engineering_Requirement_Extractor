@echo off
cd /d "C:\Users\shaki\Desktop\Orise\AI_Engineering_Designer"
echo ========================================
echo   Engineering Assistant - Config Manager
echo ========================================
echo.
echo Starting configuration manager...
echo.
echo 💡 To stop: Close this window or press Ctrl+C
echo.
call venv\Scripts\activate
streamlit run config_manager_app.py