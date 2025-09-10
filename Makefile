
# Start containers in background
up:
	docker compose up -d

# Stop containers but keep DB data
down:
	docker compose down

# Stop containers AND delete DB volume (reset DB)
reset-db:
	docker compose down -v
	docker compose up -d

# Rebuild backend image (use if dependencies change)
build:
	docker compose build --no-cache

# Run migrations
migrate:
	docker compose run --rm backend poetry run python manage.py migrate

# Show migrations for all apps
showmigrations:
	docker compose run --rm backend poetry run python manage.py showmigrations

# Show migrations for specific app (usage: make showmigrations app=orders)
showmigrations-app:
	docker compose run --rm backend poetry run python manage.py showmigrations $(app)

# Create a superuser
createsuperuser:
	docker compose run --rm backend poetry run python manage.py createsuperuser

# Open Django shell
shell:
	docker compose run --rm backend poetry run python manage.py shell

# Tail logs from backend
logs:
	docker compose logs -f backend