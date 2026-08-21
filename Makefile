.PHONY: all build up down test

all: down build up test

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down -v --remove-orphans

test:
	docker compose run --rm --no-deps api pytest tests