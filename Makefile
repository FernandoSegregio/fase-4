# Executa o aplicativo principal
run:
	python src/run.py

setup_db:
	python src/scripts/setup_db.py

mqtt:
	python src/mqtt_client.py

# Limpa arquivos temporários, como __pycache__
clean:
	find . -name "__pycache__" -exec rm -rf {} +

setup-mac: 
	python3 -m venv .venv && source .venv/bin/activate && pip install -U pip && pip install -r requirements.txt && cd PlatformIO/ && pip install -U platformio && pio pkg install -l "DHT sensor library for ESPx"

setup-linux: 
	python3 -m venv .venv && source .venv/bin/activate && pip install -U pip && pip install -r requirements.txt && cd PlatformIO/ && pip install -U platformio && pio pkg install -l "DHT sensor library for ESPx"

setup-windows:
	python -m venv .venv && .\.venv\Scripts\activate && pip install -U pip && pip install -r requirements.txt & cd PlatformIO/Projects/agric_machine && pip install -U platformio && pio lib install "DHT sensor library for ESPx"

prio-start:
	cd PlatformIO/ && pio run --target clean && pio run
