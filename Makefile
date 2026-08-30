.PHONY: install build up down logs test lint

install:
	# Установка Python-зависимостей локально
	cd shared && pip install -r requirements.txt && pip install -e .
	cd gateway && pip install -r requirements.txt && pip install -e ../shared
	cd workers/spam_worker && pip install -r requirements.txt && pip install -e ../../shared
	cd webui/backend && pip install -r requirements.txt && pip install -e ../../shared
	cd webui/frontend && npm install

build:
	./scripts/build.sh

up:
	docker-compose -f deploy/docker-compose.yml up -d

down:
	docker-compose -f deploy/docker-compose.yml down

logs:
	docker-compose -f deploy/docker-compose.yml logs -f

test:
	./scripts/test.sh

lint:
	pre-commit run --all-files