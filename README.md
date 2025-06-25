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

  <h3 align="center">dicom4ortho 0.5.1</h3>

  <p align="center">
    A Python library to create fully defined orthodontic photographs in DICOM.
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
- [About The Project](#about-the-project)
  - [Built With](#built-with)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Validation with dicom3tools](#validation-with-dicom3tools)
- [Usage](#usage)
- [Known Issues](#known-issues)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)


<!-- ABOUT THE PROJECT -->
## About The Project

The DICOM standard is ready for any developer in the orthodontic community to
implement. However, it can be complicated and implementation can be time
consuming. We want to create a proof of concept to demonstrate how to
properly store orthodontic visible light images (aka photographs) using
DICOM, while ensuring all codes (necessary to uniquely identify each image
type) are in the proper place.

Here's why:

* Your time should be focused on creating something amazing.
* Being able to import and export DICOM images to and from your orthodontic
  software will open doors to you and the orthodontic provider.
* No one software will serve all orthodontic providers completely. Adding
  interoperability will allow your product to integrate with others, giving
  additional value to your solution.

You may suggest changes by forking this repo and creating a pull request or
opening an issue. Thanks to all the people have have contributed to this
project!

A list of commonly used resources that we find helpful are listed in the
acknowledgements.

### Built With

* [pydicom](https://pydicom.github.io/)
* [pynetdicom](https://pydicom.github.io/pynetdicom/)
* [pillow](https://python-pillow.org/)
* [dicom3tools](https://www.dclunie.com/dicom3tools.html)

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

    $ pytest --cov=dicom4ortho tests/

To run a specific test file:

    $ pytest test/test_cli.py

All tests are located in the `test/` directory and can be executed after installing the development dependencies.

#### Docker for Integration Tests

Some tests require Docker to run integration tests with an Orthanc DICOM server. 
A docker-compose file is provided in the `test/` directory.

If you're not using the Makefile, you can manually manage the Docker containers:

    $ docker compose -f ./test/docker-compose.yml up -d
    $ # Run your tests...
    $ docker compose -f ./test/docker-compose.yml down

Make sure Docker is installed and running before executing integration tests.

### Using the Makefile

The project includes a Makefile that simplifies common development tasks:

    $ make test              # Run all tests (automatically handles Docker)
    $ make clean             # Clean build artifacts
    $ make build             # Build the package (includes linting and testing)
    $ make lint              # Run linter on the code
    $ make all               # Clean and build
    $ make install-dev       # Install development tools including dicom3tools
    $ make update_resources  # Update resource files from source
    $ make deploy            # Deploy to PyPI

The Makefile handles Docker for you when running tests. It starts the required Docker containers before running tests and shuts them down afterward.

### Validation with dicom3tools

The dicom3tools are used to validate and is only used when the `--validate`
option is used. This is just a conveninece wrapper for debugging, and it's
installation is not necessary for normal operation.

The [dicom3tools](https://www.dclunie.com/dicom3tools.html) can be installed
from compiled binaries, which are available for macOS and Windows.

Once installed, point `DICOM3TOOLS_PATH` in `config.py` to the installation
of the dicom3tools.

<!-- USAGE EXAMPLES -->
## Usage

The official documentation of this project is available on line
[here](https://open-ortho.github.io/dicom4ortho). Source code for the
documentation is in this repository under the `gh-pages` branch.

The DICOM images require a lot of information which is not contained in a
flat PNG or JPEG image. This information would, in a production environment,
usually come from the practice management software, or photo management
software.

The easiest way to feed this information to `dicom4ortho`'s CLI is using a
CSV file. You can find an example CSV file [here](resources/example/input_from.csv)

Once installed, if necessary, start the virtual environment:

    pipenv shell

then use dicom4ortho like this:

    $ dicom4ortho <filename>

Where `filename` should be a `.csv` file. Passing a single image file with
metadata through arguments is planned for future implementations.

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
[example-csv-url]: resources/example/input_from.csv
