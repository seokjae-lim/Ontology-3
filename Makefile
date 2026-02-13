up:
	docker compose up --build -d

down:
	docker compose down -v

migrate:
	docker compose run --rm backend alembic upgrade head

seed:
	docker compose run --rm backend python seed.py

test:
	docker compose run --rm backend pytest -q
