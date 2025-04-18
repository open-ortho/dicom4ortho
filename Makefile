MAIN = dicom4ortho
D3TOOLS_DIR = modules/dicom3tools
D3TOOLS_VERSION = 1.00.snapshot.20230225185712
D3TOOLS_BASE_URL = https://www.dclunie.com/dicom3tools/workinprogress/macexe/dicom3tools_
D3TOOLS_FILE = dicom3tools.zip
URL_DENT_OIP_LATEST_ROOT = https://raw.githubusercontent.com/open-ortho/dent-oip/latest
URL_CODES = $(URL_DENT_OIP_LATEST_ROOT)/source/tables/codes.csv
URL_VIEWS = $(URL_DENT_OIP_LATEST_ROOT)/source/tables/views.csv
CODES = $(MAIN)/resources/codes.csv
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

.PHONY: default
default: clean build

.PHONY: lint
lint:
	$(LINTER) $(MAIN)

# install-dev is required here, but it cannot ruun from pipenv environment because it relies on sudo, i guess its a new security feature. So install-dev is a manual step which needs to be run before run outside of pipenv.
.PHONY: test
test:
	docker compose -f ./test/docker-compose.yml up -d
	sleep 3
	python3 -m unittest
	docker compose -f ./test/docker-compose.yml down

.PHONY: clean
clean:
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
build: lint test $(DIST) update_resources
	python3 -m build

.PHONY: update_resources
update_resources:
	@# Download views.csv only if it has changed
	curl --silent -z $(VIEWS) -o $(VIEWS) $(URL_VIEWS)
	@# Download codes.csv only if it has changed
	curl --silent -z $(CODES) -o $(CODES) $(URL_CODES)
	@# Check if views.csv has "VER" and is different from the repository state
	@if [ -f $(VIEWS) ] && grep -q "VER" $(VIEWS) && ! git diff --quiet --exit-code $(VIEWS); then \
	    git add $(VIEWS); \
	    git commit -m "Update views.csv"; \
	fi
	@# Check if codes.csv has "__version__" and is different from the repository state
	@if [ -f $(CODES) ] && grep -q "__version__" $(CODES) && ! git diff --quiet --exit-code $(CODES); then \
	    git add $(CODES); \
	    git commit -m "Update codes.csv"; \
	fi

.PHONY: deploy
deploy:
	echo "Deplyoing to PyPi."
	echo "To deploy, make sure you have a token saved in ~/.pypirc . See https://pypi.org/manage/account/token/?selected_project=dicom4ortho"
	python3 -m twine upload --repository pypi dist/*

.PHONY: all
all: clean build

.PHONY: install-dev
install-dev: $(D3TOOLS_DIR)
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