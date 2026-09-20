.PHONY: setup fetch atoms export api web build deploy test lint check review

setup:
	cd backend && uv sync
	cd frontend && npm install

fetch:
	cd backend && uv run python scripts/fetch_geo.py

atoms:
	cd backend && uv run python scripts/build_atoms.py

export:
	cd backend && uv run python scripts/export_static.py

api:
	cd backend && uv run uvicorn app.main:app --reload --port 8000

web:
	cd frontend && npm run dev

build: export
	cd frontend && npm run build

deploy: build
	cd frontend && npx wrangler deploy

test:
	cd backend && uv run pytest -q

review:
	cd backend && uv run python scripts/review_status.py

lint:
	cd backend && uv run ruff check . && uv run ruff format --check .

check: lint test export
	@test -z "$$(git status --porcelain -- frontend/static/api)" \
		|| { echo "frontend/static/api is stale; commit the re-export"; exit 1; }
	cd frontend && npm run check && npx vite build
