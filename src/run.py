# run.py
import subprocess
import sys
import time
import os

def run_apps():
    try:
        # Iniciar MQTT Client em background
        mqtt_process = subprocess.Popen([
            sys.executable,
            "src/mqtt_client.py"
        ])
        
        # Iniciar Streamlit App
        streamlit_process = subprocess.Popen([
            "streamlit",
            "run",
            "src/app.py"
        ])
        
        # Manter processos rodando
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nEncerrando aplicações...")
        mqtt_process.terminate()
        streamlit_process.terminate()
        
    except Exception as e:
        print(f"Erro: {e}")
        if 'mqtt_process' in locals():
            mqtt_process.terminate()
        if 'streamlit_process' in locals():
            streamlit_process.terminate()

if __name__ == "__main__":
    run_apps()