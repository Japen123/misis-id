.PHONY: help install install-dev lint format clean build upload

help: ## Показать справку
	@echo "Доступные команды:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Установить пакет
	pip install -e .

install-dev: ## Установить пакет в режиме разработки
	pip install -e ".[dev]"

lint: ## Проверить код линтерами
	flake8 misis_id
	mypy misis_id

format: ## Форматировать код
	black misis_id
	isort misis_id

clean: ## Очистить временные файлы
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build: clean ## Собрать пакет
	python -m build

upload: build ## Загрузить пакет в PyPI
	twine upload dist/*

check: lint ## Проверить код

all: format check build ## Форматировать, проверить, собрать
