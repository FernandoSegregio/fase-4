# Executa o aplicativo principal
run:
	python src/app.py

setup_db:
	python src/scripts/setup_db.py

mqtt:
	python src/mqtt_client.py

# Limpa arquivos temporários, como __pycache__
clean:
	find . -name "__pycache__" -exec rm -rf {} +

setup1:
	python -m venv .venv && source .venv/bin/activate && pip install -U pip && cd PlatformIO/Projects/agric_machine && pip install -U platformio && pio lib install "DHT sensor library for ESPx"

setup2:
	python -m venv .venv && .\.venv\Scripts\activate && pip install -U pip && pip install -r requirements.txt & cd PlatformIO/Projects/agric_machine && pip install -U platformio && pio lib install "DHT sensor library for ESPx"

start:
	cd PlatformIO/Projects/agric_machine && pio run --target clean && pio run
