# Makefile
setup:
	pip install -r requirements.txt
	pre-commit install

run:
	docker-compose up -d --build

stop:
	docker-compose down

logs:
	docker logs -f barkingdog_scanner

lint:
	ruff check . --fix
