MAIN = dicom4ortho
D3TOOLS_DIR = modules/dicom3tools
D3TOOLS_VERSION = 1.00.snapshot.20230225185712
D3TOOLS_BASE_URL = https://www.dclunie.com/dicom3tools/workinprogress/macexe/dicom3tools_
D3TOOLS_FILE = dicom3tools.zip
URL_DENT_OIP_LATEST_ROOT = https://raw.githubusercontent.com/open-ortho/dent-oip/latest
URL_VIEWS = $(URL_DENT_OIP_LATEST_ROOT)/source/tables/views.csv
VIEWS = $(MAIN)/resources/views.csv

ifeq ($(OS),Windows_NT)
	D3TOOLS_URL = $(D3TOOLS_BASE_URL)winexe_$(D3TOOLS_VERSION).zip
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Darwin)
		D3TOOLS_URL = $(D3TOOLS_BASE_URL)macexe_$(D3TOOLS_VERSION).zip
    endif
endif

DIST = ./dist


LINTER = $$(which pylint) --errors-only

.PHONY: help
help: ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help

.PHONY: default
default: clean build

.PHONY: lint
lint: ## Run linter (errors only)
	$(LINTER) $(MAIN)

# install-dev is required here, but it cannot ruun from pipenv environment because it relies on sudo, i guess its a new security feature. So install-dev is a manual step which needs to be run before run outside of pipenv.
.PHONY: test
test: ## Run unit tests (starts/stops Docker for integration tests)
	docker compose -f ./test/docker-compose.yml up -d
	sleep 3
	python3 -m unittest
	docker compose -f ./test/docker-compose.yml down

.PHONY: clean
clean: ## Remove build artifacts, caches, and egg-info
	rm -rf $(DIST) ./build
	echo "Cleaned up $(DIST) folder."
	rm -rf *.egg-info
	echo "Removed all .egg-info files."
	find . -path "*/__pycache*" -delete
	echo "Deleted all __pycache files."
	rm -rf $(D3TOOLS_DIR)

$(DIST):
	mkdir $@

.PHONY: build
build: lint test $(DIST) ## Lint, test, and build from the committed terminology lock
	python3 -m build

.PHONY: fetch_resources
fetch_resources: ## Download views.csv from upstream dent-oip
	@# See https://github.com/open-ortho/dent-oip/issues/11 — until that is resolved,
	@# run this target manually and verify generate_codes.py succeeds before committing.
	curl --silent -z $(VIEWS) -o $(VIEWS) $(URL_VIEWS)


.PHONY: update_codes
update_codes: ## Fetch authoritative terminology and regenerate _generated_codes.py
	python3 tools/generate_codes.py

.PHONY: check_codes
check_codes: ## Regenerate terminology in memory and fail when the lock has drifted
	python3 tools/generate_codes.py --check

.PHONY: deploy
deploy: ## Upload distribution to PyPI (requires ~/.pypirc token)
	echo "Deplyoing to PyPi."
	echo "To deploy, make sure you have a token saved in ~/.pypirc . See https://pypi.org/manage/account/token/?selected_project=dicom4ortho"
	python3 -m twine upload --repository pypi dist/*

.PHONY: all
all: clean build ## Clean then build

.PHONY: install-dev
install-dev: $(D3TOOLS_DIR) ## Install development dependencies (dicom3tools)
ifeq ($(UNAME_S),Linux)
install-dev:
	sudo apt-get -y install dicom3tools
	rm -f $(D3TOOLS_DIR)/dciodvfy
	ln -s /usr/bin/dciodvfy $(D3TOOLS_DIR)
else
install-dev:
	cd $(D3TOOLS_DIR) && curl $(D3TOOLS_URL) -o $(D3TOOLS_FILE) && unzip $(D3TOOLS_FILE) && rm $(D3TOOLS_FILE)
endif

$(D3TOOLS_DIR):
	mkdir -p $@
