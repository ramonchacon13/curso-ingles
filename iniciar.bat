@echo off
cd /d "C:\Users\Ramon\Documents\Default Project\curso-ingles"
echo Iniciando CursoIngles...
start "CursoIngles-Backend" cmd /k "cd /d backend && python run.py"
start "CursoIngles-Frontend" cmd /k "cd /d react-app && npm run dev"
echo.
echo Backend:  http://localhost:8080
echo Frontend: http://localhost:5173
echo.
echo Deja estas ventanas abiertas. Cierra las ventanas para detener los servidores.
echo.
pause
