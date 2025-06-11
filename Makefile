all: up

env:
	@if [ ! -f .env ]; then \
        echo "Creating .env from .env.example"; \
        cat .env.example >> .env; \
    else \
        echo ".env already exists."; \
    fi

up:
	docker-compose up --build -d

down:
	docker-compose down

restart:
	docker-compose restart bot

rebuild:
	docker-compose up --build -d --no-deps bot

logs:
	docker-compose logs -f bot

migrate:
	docker-compose exec django python manage.py makemigrations
	docker-compose exec django python manage.py migrate

admin:
	docker-compose exec django python manage.py createsuperuser

shell:
	docker-compose exec django python manage.py shell

load:
	docker-compose exec django python manage.py loaddata data.json

dump:
	docker-compose exec django python manage.py dumpdata -o data.json --indent 2 core.country

lint:
	ruff format
	ruff check --fix
	ruff format

check:
	ruff check

extract-messages:
	pybabel extract --input-dirs=. -o backend/locales/messages.pot

init-messages:
	pybabel init -i backend/locales/messages.pot -d backend/locales -D messages -l $(LANG)

update-messages:
	pybabel update -d backend/locales -D messages -i backend/locales/messages.pot

compile-messages:
	pybabel compile -d backend/locales -D messages
