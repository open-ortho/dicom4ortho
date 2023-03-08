
MAIN = dicom4ortho
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
