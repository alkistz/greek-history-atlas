.PHONY: setup fetch atoms api web test lint check

setup:
	cd backend && uv sync
	cd frontend && npm install

fetch:
	cd backend && uv run python scripts/fetch_geo.py

atoms:
	cd backend && uv run python scripts/build_atoms.py

api:
	cd backend && uv run uvicorn app.main:app --reload --port 8000

web:
	cd frontend && npm run dev

test:
	cd backend && uv run pytest -q

lint:
	cd backend && uv run ruff check . && uv run ruff format --check .

check: lint test
	cd frontend && npm run check && npx vite build
