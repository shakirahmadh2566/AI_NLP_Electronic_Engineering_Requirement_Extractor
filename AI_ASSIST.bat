@echo off
cd /d "C:\Users\shaki\Desktop\Orise\AI_Engineering_Designer"
echo ========================================
echo   Engineering Assistant - Main App
echo ========================================
echo.
echo Starting main application...
echo.
echo 💡 To stop: Close this window or press Ctrl+C
echo.
call venv\Scripts\activate
streamlit run streamlit_app.py