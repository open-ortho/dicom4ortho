
MAIN = dicom4ortho
D3TOOLS_DIR = modules/dicom3tools
D3TOOLS_VERSION = 1.00.snapshot.20230225185712
D3TOOLS_BASE_URL = https://www.dclunie.com/dicom3tools/workinprogress/macexe/dicom3tools_
D3TOOLS_FILE = dicom3tools.zip

ifeq ($(OS),Windows_NT)
	D3TOOLS_URL = $(D3TOOLS_BASE_URL)winexe_$(D3TOOLS_VERSION).zip
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Linux)
		D3TOOLS_URL = $(D3TOOLS_BASE_URL)macexe_$(D3TOOLS_VERSION).zip
    endif
    ifeq ($(UNAME_S),Darwin)
		D3TOOLS_URL = $(D3TOOLS_BASE_URL)macexe_$(D3TOOLS_VERSION).zip
    endif
endif

DIST = ./dist


LINTER = $$(which pylint) --errors-only


.PHONY: lint
lint:
	$(LINTER) setup.py
	$(LINTER) $(MAIN)

.PHONY: test
test:
	python -m unittest

.PHONY: clean
clean:
	rm -rf $(DIST)
	echo "Cleaned up $(DIST) folder."
	rm -rf *.egg-info
	echo "Removed all .egg-info files."
	rm -f test/resources/*.dcm
	echo "Removed *.dcm files in test/resources."
	find . -path '*/__pycache*' -delete
	echo "Deleted all __pycache files."

$(DIST):
	mkdir $@

.PHONY: build
build: lint test $(DIST)
	python -m setup sdist

.PHONY: deploy
deploy:
	echo "Deplyoing to PyPi."
	python -m twine upload --repository pypi dist/*

.PHONY: all
all: clean build

.PHONY: install-dev
install-dev: $(D3TOOLS)

$(D3TOOLS_DIR):
	mkdir -p $@
	cd $@ && curl $(D3TOOLS_URL) -o $(D3TOOLS_FILE) && unzip $(D3TOOLS_FILE) && rm $(D3TOOLS_FILE)