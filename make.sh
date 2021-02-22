#!/bin/sh

MAIN="dicom4ortho"
DIST="./dist"


LINTER="$(which pylint)" || {
    echo "Cannot find xmllint. Install first."
    exit 1
}
PANDOC="$(which pandoc)" || {
    echo "Cannot find pandoc. Install first"
    exit 1
}

print_help() {
    echo
    echo "Available commands:"
    echo "  clean   : Remove dist/ folders for modules"
    echo "  build   : Builds distribution packages in dist/"
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
all)
    clean || exit
    build || exit
    exit
    ;;
*) # Default case: If no more options then break out of the loop.
    print_help ;;
esac

# Rest of the program here.
