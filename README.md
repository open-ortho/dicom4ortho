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

  <h3 align="center">dicom4ortho 0.3.2</h3>

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
  - [CSV Image file format](#csv-image-file-format)
    - [patient\_firstname](#patient_firstname)
    - [patient\_lastname](#patient_lastname)
    - [patient\_id](#patient_id)
    - [patient\_sex](#patient_sex)
    - [patient\_birthdate](#patient_birthdate)
    - [dental\_provider\_firstname](#dental_provider_firstname)
    - [dental\_provider\_lastname](#dental_provider_lastname)
    - [image\_type](#image_type)
    - [manufacturer](#manufacturer)
    - [input\_image\_filename](#input_image_filename)
    - [study\_instance\_uid](#study_instance_uid)
    - [study\_description](#study_description)
    - [series\_instance\_uid](#series_instance_uid)
    - [series\_description](#series_description)
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
* [pillow](https://python-pillow.org/)
* [dicom3tools](https://www.dclunie.com/dicom3tools.html)

<!-- GETTING STARTED -->
## Getting Started

Like any other Python module, install the module than use it. There is a CLI
interface as well.

### Prerequisites

- An installation of Python 3+.
- optional: [dicom3tools](https://www.dclunie.com/dicom3tools.html)

### Installation

Install unsing pipenv by running

    $ pipenv install dicom4ortho

Install using pip by running

    $ pip install dicom4ortho

Only Python 3+ is supported

### Validation with dicom3tools

The dicom3tools are used to validate and is only used when the `--validate`
option is used. This is just a conveninece wrapper for debugging, and it's
installation is not necessary for normal operation.

The [dicom3tools](https://www.dclunie.com/dicom3tools.html) can be installed
from compiled binaries, which are available for macOS and Windows.

Once installed, point `DICOM3TOOLS_PATH` in `defaults.py` to the installation
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

### CSV Image file format

The CSV file should be:

- with `,` as separator
- `UTF-8` encoded

Each CSV file should containt the following columns (header)

#### patient_firstname

Patient first name. First part of DICOM tag `(0010, 0010) Patient's Name`.

#### patient_lastname

Patient last name. Second part of DICOM tag `(0010, 0010) Patient's Name`.

#### patient_id

Patient ID. DICOM `(0010, 0020) Patient ID` tag.

#### patient_sex

Patient's gender. DICOM `(0010, 0040) Patient's Sex` tag.

#### patient_birthdate

Patient's date of birth in YYYY-MM-DD format. DICOM `(0010, 0030) Patient's
Birth Date` tag.

#### dental_provider_firstname

First name of orthodontic (or dental) provider. First part of DICOM `(0008,
0090) Referring Physician's Name` tag.

#### dental_provider_lastname

Last name of orthodontic (or dental) provider. Second part of DICOM `(0008,
0090) Referring Physician's Name` tag.

#### image_type

Image type as defined by ADA SCDI WP-1100. Type

    dicom4ortho list-image-types

for a list of allowed image types.

#### manufacturer

Manufacturer of Camera. For example, when using an iPhone, use `Apple`
here. Overrides input file's EXIF metadata.

#### input_image_filename

Full path of flat JPG/PNG/TIFF image file to use as input.

#### study_instance_uid

The unique identifier that distinguishes this study from any other study. For
orthodontic purposes, all images taken during the same patient visit, should
go under the same study, thus have the same study UID.

This is a DICOM UID object and goes into the DICOM `(0020, 000d) Study
Instance UID` tag. The exact format is defined in [DICOM Part 5 Data
Structures and Encoding - Value Encoding - Value
Representation](http://dicom.nema.org/medical/dicom/current/output/html/part05.html#sect_6.2)


#### study_description

A description for this specific study. For orthodontic purposes, this value
could be something like 'Initial Visit'.

This is a DICOM UID object and goes into the DICOM `(0008, 1030) Study
Description`. Maximum 64 characters are allowed, as defined the [DICOM LO
VR](http://dicom.nema.org/medical/dicom/current/output/html/part05.html#sect_6.2)


#### series_instance_uid

The unique identifier that distinguishes this series from any other series.
For orthodontic purposes, all images taken with the same imaging device (for
photographs, this would be the camera) and during the same study (hence
appointment visit) should be part of the same series, thus have the same
series UID.

This is a DICOM UID object and goest into the DICOM `(0020, 000e) Series
Instance UID` tag. The exact format is defined in [DICOM Part 5 Data
Structures and Encoding - Value Encoding - Value
Representation](http://dicom.nema.org/medical/dicom/current/output/html/part05.html#sect_6.2)

#### series_description

A description for this specific series. For orthodontic purposes, this value
could be something like 'Orthodontic Intraoral Series'.

This is a DICOM UID object and goes into the DICOM `(0008, 103e) Series
Description`. Maximum 64 characters are allowed, as defined the [DICOM LO
VR](http://dicom.nema.org/medical/dicom/current/output/html/part05.html#sect_6.2)

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
