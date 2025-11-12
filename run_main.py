# run_app.py
import socket
import subprocess

# Detecta IP local da máquina
ip_local = socket.gethostbyname(socket.gethostname())

print(f"🌐 Iniciando Streamlit com IP local: {ip_local}")
subprocess.run(["streamlit", "run", "main.py", "--server.address", ip_local])
