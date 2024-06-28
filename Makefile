
MAIN = dicom4ortho
D3TOOLS_DIR = modules/dicom3tools
D3TOOLS_VERSION = 1.00.snapshot.20230225185712
D3TOOLS_BASE_URL = https://www.dclunie.com/dicom3tools/workinprogress/macexe/dicom3tools_
D3TOOLS_FILE = dicom3tools.zip

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
	$(LINTER) setup.py
	$(LINTER) $(MAIN)

.PHONY: test
test: install-dev
	docker compose -f ./test/docker-compose.yml up -d
	sleep 3
	python3 -m unittest
	docker compose -f ./test/docker-compose.yml down

.PHONY: clean
clean:
	rm -rf $(DIST)
	echo "Cleaned up $(DIST) folder."
	rm -rf *.egg-info
	echo "Removed all .egg-info files."
	find . -path "*/__pycache*" -delete
	echo "Deleted all __pycache files."
	rm -rf $(D3TOOLS_DIR)

$(DIST):
	mkdir $@

.PHONY: build
build: lint test $(DIST)
	python3 -m setup sdist


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