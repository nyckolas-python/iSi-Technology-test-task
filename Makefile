DOCKER_COMPOSE=docker-compose

# Default target
.PHONY: help
help:  ## Display this help
	@echo "Usage: make [target] ..."
	@echo
	@echo "Targets:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / { printf "  %-15s %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

.PHONY: init
init: env up migrate createsuperuser fixtures  ## Initialize the project

.PHONY: env
env:  ## Create .env file from .env.example
	cp .env.example .env

.PHONY: up
up:  ## Start the Docker Compose services
	$(DOCKER_COMPOSE) up -d

.PHONY: down
down:  ## Stop the Docker Compose services
	$(DOCKER_COMPOSE) down

.PHONY: logs
logs:  ## Tail the logs of the Docker Compose services
	$(DOCKER_COMPOSE) logs -f

.PHONY: shell
sh:  ## Get a shell inside the app container
	$(DOCKER_COMPOSE) exec my_project_app bash

.PHONY: migrate
migrate:  ## Run Django database migrations
	$(DOCKER_COMPOSE) exec my_project_app python manage.py migrate

.PHONY: migrations
migrations:  ## Create new Django migrations
	$(DOCKER_COMPOSE) exec my_project_app python manage.py makemigrations

.PHONY: createsuperuser
createsuperuser:  ## Create a Django superuser
	$(DOCKER_COMPOSE) exec my_project_app python manage.py createsuperuser

.PHONY: load_fixtures
fixtures:  ## Load fixtures
	$(DOCKER_COMPOSE) exec my_project_app python manage.py setup_test_data

.PHONY: collectstatic
collectstatic:  ## Collect static files
	$(DOCKER_COMPOSE) exec my_project_app python manage.py collectstatic --noinput

.PHONY: test
test:  ## Run Django tests
	$(DOCKER_COMPOSE) exec my_project_app python manage.py test

.PHONY: clean
clean:  ## Clean up unused Docker resources
	docker system prune -f