@echo on

set project_dir=C:\Users\Thomas\Documents\Spiele\Shooter\shooter\shooter
set virtual_environment_dir=venv

cd "%project_dir%"

call %virtual_environment_dir%\Scripts\activate.bat

python pgzblaster.py

pause