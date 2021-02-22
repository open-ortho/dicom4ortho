#!/bin/sh

MAIN="dicom4ortho"
DIST="./dist"


LINTER="$(which pylint)" || {
    echo "Cannot find xmllint. Install first."
    exit 1
}

print_help() {
    echo
    echo "Available commands:"
    echo "  clean   : Remove dist/ folders for modules"
    echo "  build   : Builds distribution packages in dist/"
    echo "  deploy  : Deploy packages in dist/ to PyPi"
    echo "  all     : clean then build"
    echo
}

lint() {
    $LINTER -E setup.py
    $LINTER -E "${MAIN}"
}

clean() {
    rm -rf "${DIST}" || exit
    rm -rf *.egg-info
    find . -path '*/__pycache*' -delete
    echo "Cleaned up ${DIST} folder."
}

build() {
    mkdir ${DIST} 2> /dev/null
    lint || exit
    python -m setup.py sdist
}

deploy() {
    echo "Deploy not implemented."
    python -m twine upload --repository pypi dist/*
}

all() {
    clean || exit
    build || exit
}

case $1 in
clean)
    clean
    exit
    ;;
build)
    build
    exit
    ;;
deploy)
    deploy
    exit
    ;;
all)
    clean || exit
    build || exit
    exit
    ;;
*) # Default case: If no more options then break out of the loop.
    print_help ;;
esac

# Rest of the program here.
