[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
<br />
<p align="center">
  <a href="https://github.com/open-ortho/dicom4ortho">
    <img src="https://raw.githubusercontent.com/open-ortho/dicom4ortho/master/images/open-ortho.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">dicom4ortho 0.5.4-dev</h3>

  <p align="center">
    DICOM functionality for orthodontic photographs.
    <br />
    <a href="https://open-ortho.github.io/dicom4ortho/"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/open-ortho/dicom4ortho">View Demo</a>
    ·
    <a href="https://github.com/open-ortho/dicom4ortho/issues">Report Bug</a>
    ·
    <a href="https://github.com/open-ortho/dicom4ortho/issues">Request Feature</a>
  </p>
</p>

<!-- TABLE OF CONTENTS -->

- [Introduction](#introduction)
- [About The Project](#about-the-project)
  - [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Validation with dicom3tools](#validation-with-dicom3tools)
- [Repository layout](#repository-layout)
- [Usage](#usage)
- [Known Issues](#known-issues)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)

## Introduction

`dicom4ortho` is an open-source library: a reusable software component
for developers building applications that store and exchange dental photographs.
Python is the current implementation; other language implementations may expose
idiomatic APIs while sharing the same functional goals.

Dental providers, especially orthodontists, take different types of patient
photographs to document anatomy and monitor treatment. These include full-face
and profile views, photographs inside the mouth, and close-ups of particular
structures. Each photograph needs to be distinguished by what it shows and how
it was taken, not just by its filename. Software exchanging these images
needs a shared way to describe them so the receiving application can identify
the photograph type without relying on another application's naming conventions.

[DICOM (Digital Imaging and Communications in Medicine)][dicom-overview] is the
international standard for medical images and related information. It defines
how to store and exchange image pixels together with structured attributes
(metadata), such as patient identity, anatomy, viewing direction, and acquisition
time. DICOM is not limited to X-rays and scans; it also supports ordinary
visible-light photographs.

The **American Dental Association (ADA)** is a professional organization for
dentists that also develops dental standards. It is
[accredited by the **American National Standards Institute (ANSI)**][ada-standards-program]
to develop national standards for dentistry. The documents relevant to this
library have different roles:

- **ADA 1100** defines 73 commonly used orthodontic photograph types, with line
  drawings illustrating the views.
- **ADA 1114** defines requirements for using DICOM for dental images and refers
  to ADA 1100 for the orthodontic photograph types.
- **Draft ADA-1107** is an implementation profile: a set of rules explaining how
  to apply these standards together to a particular clinical workflow. It is
  not yet published. `dicom4ortho` directly implements this draft profile, so its
  support for ADA 1100 and ADA 1114 is through ADA-1107.

DICOM [change proposals (CPs)][dicom-change-proposals] are documents proposing
corrections, clarifications, or small additions to the standard. Approved
proposals are incorporated into the standard.
[DICOM CP 1570](https://dicom.nema.org/Dicom/News/March2025/docs/cpack130/cp1570.pdf)
added the dental acquisition attributes and codes used by the profile. These
allow anatomy and the clinical circumstances of taking a photograph to be
described in a standardized way. The ADA 1100 photograph types and their
mappings to **SNOMED CT (Systematized Nomenclature of Medicine — Clinical Terms)**
are published at https://terminology.open-ortho.org/. SNOMED CT is a clinical
terminology that gives concepts, such as anatomical structures, shared coded
identifiers rather than relying only on free-text descriptions.

An **Information Object Definition (IOD)** specifies the required and optional
attributes for a particular kind of DICOM object. `dicom4ortho` builds DICOM
datasets (collections of attributes that can include image data) according to
these definitions and the draft profile. It pre-populates the anatomic and
clinical attributes derived from the selected image type. The shared functionality
expected of each implementation is to:

- create a DICOM image from a photograph, patient details, and an image type;
- create a pre-populated DICOM dataset template from an image type;
- extract the photograph views declared in a supplied DICOM image instance or
  prescribed in a Modality Worklist dataset.

The [shared functional contract](docs/API_CONTRACT.md) describes these capabilities
and their test-adapter boundary. Shared conformance tests are planned; this does not
claim that every implementation already supports every case.

<!-- ABOUT THE PROJECT -->

## About The Project

Implementing these standards directly can be time-consuming. The project
provides reusable code and a proof of concept so developers can build on tested
mappings rather than reconstructing every DICOM requirement themselves.

Here's why:

- Your time should be focused on creating something amazing.
- Being able to import and export DICOM images to and from your orthodontic
  software will open doors to you and the orthodontic provider.
- No one software will serve all orthodontic providers completely. Adding
  interoperability will allow your product to integrate with others, giving
  additional value to your solution.

You may suggest changes by forking this repo and creating a pull request or
opening an issue. Thanks to all the people have have contributed to this
project!

A list of commonly used resources that we find helpful are listed in the
acknowledgements.

### Built With

- [pydicom](https://pydicom.github.io/)
- [pynetdicom](https://pydicom.github.io/pynetdicom/)
- [pillow](https://python-pillow.org/)
- [dicom3tools](https://www.dclunie.com/dicom3tools.html)

<!-- GETTING STARTED -->

## Getting Started

Like any other Python module, install the module and use it. There is a CLI
interface as well.

### Prerequisites

- An installation of Python 3.10+.
- optional: [dicom3tools](https://www.dclunie.com/dicom3tools.html)

### Installation

Install using pip by running:

    $ pip install dicom4ortho

If you're a developer working on the project, you can install with dev dependencies:

    $ pip install dicom4ortho[dev]

The project uses pyproject.toml for package configuration and build settings.

### Creating a Virtual Environment

It's recommended to use a virtual environment for development:

    $ python -m venv venv
    $ source venv/bin/activate  # On Windows use: venv\Scripts\activate

    # Install the package in development mode
    $ pip install -e .

    # To install with development dependencies
    $ pip install -e ".[dev]"

### Building from source

To build the package from source:

    $ python -m build

This will create distribution packages in the `dist/` directory.

### Running Tests

To run all tests in the project:

    $ pytest

To run tests with coverage report:

    $ pytest --cov=dicom4ortho python/test/

To run a specific test file:

    $ pytest python/test/test_cli.py

Python tests are located in `python/test/`. For explicit unittest discovery from
the repository root, run:

    $ PYTHONPATH=python python -m unittest discover -s python/test -t python

#### Docker for Integration Tests

Some tests require Docker to run integration tests with an Orthanc DICOM server.
A docker-compose file is provided in the `python/test/` directory.

If you're not using the Makefile, you can manually manage the Docker containers:

    $ docker compose -f ./python/test/docker-compose.yml up -d
    $ # Run your tests...
    $ docker compose -f ./python/test/docker-compose.yml down

Make sure Docker is installed and running before executing integration tests.

### Using the Makefile

The project includes a Makefile that simplifies common development tasks:

    $ make test              # Run all tests (automatically handles Docker)
    $ make clean             # Clean build artifacts
    $ make build             # Build the package (includes linting and testing)
    $ make lint              # Run linter on the code
    $ make all               # Clean and build
    $ make install-dev       # Install development tools including dicom3tools
    $ make update_codes      # Refresh the committed terminology lock
    $ make check_codes       # Detect upstream terminology drift without writing
    $ make deploy            # Deploy to PyPI

The Makefile handles Docker for you when running tests. It starts the required Docker containers before running tests and shuts them down afterward.
Normal package builds, tests, and runtime use the committed terminology lock
and do not require network access. `make update_codes` is an explicit
maintainer operation that loads DICOM CIDs from NEMA FHIR ValueSets, DCM
concept names from NEMA's `dcm.owl` ontology, ADA image types from Open Ortho,
and the DENT-OIP view layout. It records each observed source URL and SHA-256
in the lock; FHIR resources additionally record their observed version and
date. Review the generated diff before committing it. `make check_codes`
performs the same validation in memory and fails if the committed lock differs,
which supports scheduled terminology-drift checks without adding network I/O to
normal builds.

See [the terminology pipeline and compatibility baseline](docs/TERMINOLOGY.md)
for the exact source roles, reviewed lock checksum, coding changes, and the
separate future ADA-1107 package migration.

### Validation with dicom3tools

The dicom3tools are used to validate and is only used when the `--validate`
option is used. This is just a conveninece wrapper for debugging, and it's
installation is not necessary for normal operation.

The [dicom3tools](https://www.dclunie.com/dicom3tools.html) can be installed
from compiled binaries, which are available for macOS and Windows.

Once installed, point `DICOM3TOOLS_PATH` in `config.py` to the installation
of the dicom3tools.

<!-- USAGE EXAMPLES -->

## Repository layout

The Python implementation, tests, and examples live under [`python/`](python/).
Root `pyproject.toml`, Make targets, and release tooling remain the entry points:
`pip install -e ".[dev]"`, `python -m build`, and `make build` still run from the
repository root and produce the existing package artifacts in `dist/`.

This is a layout refactor only: no new functionality or shared executable core.
Future language implementations will have independent runtime code and builds.
See [the repository layout and implementation boundaries](docs/REPOSITORY_LAYOUT.md).

## Usage

The official documentation of this project is available on line
[here](https://open-ortho.github.io/dicom4ortho). Source code for the
documentation is in this repository under the `gh-pages` branch.

The DICOM images require a lot of information which is not contained in a
flat PNG or JPEG image. This information would, in a production environment,
usually come from the practice management software, or photo management
software.

The easiest way to feed this information to `dicom4ortho`'s CLI is using a
CSV file. You can find an executable example CSV file
[here](python/examples/input_from.csv).

Once installed, if necessary, start the virtual environment:

    pipenv shell

then use dicom4ortho like this:

    $ dicom4ortho <filename>

Where `filename` should be a `.csv` file. Passing a single image file with
metadata through arguments is planned for future implementations.

### Orthodontic Treatment Progress

`dicom4ortho` records treatment progress as a day offset from a clinical event.
See the [treatment progress documentation][treatment-progress-docs] for usage and examples.

### Practice personnel

Use `dental_provider_firstname` and `dental_provider_lastname` for the
orthodontist or dentist responsible for treatment. They are encoded as DICOM
`PhysiciansOfRecord`. Use `operator_firstname` and `operator_lastname` for the
clinical staff member who acquired the photographs; they are encoded as DICOM
`OperatorsName`.

An actual referring physician is copied from `ReferringPhysicianName` in a
Modality Worklist. The requesting physician remains part of the worklist order
and is linked through the request identifiers rather than copied into the
baseline VL Photographic Image IOD.

generate a new UID for DICOM usage with this root:

    $ d4o_generate

## Known Issues

Please check the [Implementation Status](docs/IMPLEMENTATION_STATUS.md)
document.

<!-- ROADMAP -->

## Roadmap

See the [open issues](https://github.com/open-ortho/dicom4ortho/issues) for a list of proposed features (and known issues).

<!-- CONTRIBUTING -->

## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a [Pull Request](https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request)

<!-- LICENSE -->

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for more information.

<!-- CONTACT -->

## Contact

Toni Magni- [@zgypa](https://twitter.com/zgypa) - open-ortho@afm.co

Project Link: [https://github.com/open-ortho/dicom4ortho](https://github.com/open-ortho/dicom4ortho)

<!-- ACKNOWLEDGEMENTS -->

## Acknowledgements

- [DICOM](https://www.webpagefx.com/tools/emoji-cheat-sheet)
- [American Dental Association Standards Committee for Dental Informatics](https://www.ada.org/en/science-research/dental-standards/standards-committee-on-dental-informatics)

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/open-ortho/dicom4ortho.svg?style=for-the-badge
[contributors-url]: https://github.com/open-ortho/dicom4ortho/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/open-ortho/dicom4ortho.svg?style=for-the-badge
[forks-url]: https://github.com/open-ortho/dicom4ortho/network/members
[stars-shield]: https://img.shields.io/github/stars/open-ortho/dicom4ortho.svg?style=for-the-badge
[stars-url]: https://github.com/open-ortho/dicom4ortho/stargazers
[issues-shield]: https://img.shields.io/github/issues/open-ortho/dicom4ortho.svg?style=for-the-badge
[issues-url]: https://github.com/open-ortho/dicom4ortho/issues
[license-shield]: https://img.shields.io/github/license/open-ortho/dicom4ortho.svg?style=for-the-badge
[license-url]: https://github.com/open-ortho/dicom4ortho/blob/master/LICENSE
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/open-ortho
[product-screenshot]: images/screenshot.png
[example-csv-url]: python/examples/input_from.csv
[treatment-progress-docs]: https://open-ortho.github.io/dicom4ortho/usage.html#orthodontic-treatment-progress
[dicom-overview]: https://www.dicomstandard.org/about
[ada-standards-program]: https://www.ada.org/resources/practice/dental-standards/ada-standards-program-overview
[dicom-change-proposals]: https://www.dicomstandard.org/submitcp
