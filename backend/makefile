# Variables
PYTHON := python3
PIP := $(PYTHON) -m pip
FLASK := $(PYTHON) -m flask

# Target: Install dependencies
.PHONY: install
install:
	$(PYTHON) -m venv .backendEnv
	. .backendEnv/bin/activate
	$(PIP) install -r requirements.txt

# Target: Run the Flask development server
run:
	$(FLASK) --app main run

# Target: Run unit tests
test:
	$(PYTHON) -m pytest -s tests/

# Target: Clean up
clean:
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -delete

# Target: Help
help:
	@echo "Available targets:"
	@echo "  install    : Install project dependencies"
	@echo "  run        : Run the Flask development server"
	@echo "  test       : Run unit tests"
	@echo "  clean      : Clean up generated files"
	@echo "  help       : Display this help message"