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
    <img src="images/open-ortho.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">dicom4ortho</h3>

  <p align="center">
    A Python library to create fully defined orthodontic photographs in DICOM.
    <br />
    <a href="https://github.com/open-ortho/dicom4ortho/docs"><strong>Explore the docs »</strong></a>
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
- [Usage](#usage)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)
- [Acknowledgements](#acknowledgements)


<!-- ABOUT THE PROJECT -->
## About The Project

[![dicom4ortho Screen Shot][product-screenshot]](https://example.com)

The DICOM standard is there and ready for any developer in the orthodontic
community to implement. However, they can be complicated and implementation
can be time consuming. We wanted to create a proof of concept to demonstrate
how to properly store orthodontic visible light images (aka photographs)
using DICOM, while ensuring all necessary codes to uniquely identify each
image type are in the proper place.

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

A list of commonly used resources that I find helpful are listed in the
acknowledgements.

### Built With

* [pydicom](https://pydicom.github.io/)
* [pillow](https://python-pillow.org/)

<!-- GETTING STARTED -->
## Getting Started

Like any other Python module, install the module than use it. There is a CLI
interface as well.

### Prerequisites

An installation of Python 3+.

### Installation

Install unsing pipenv by running

    $ pipenv install dicom4ortho

Install using pip by running

    $ pip install dicom4ortho

Only Python 3+ is supported

<!-- USAGE EXAMPLES -->
## Usage

Once installed, 
_For more examples, please refer to the [Documentation](https://example.com)_

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
5. Open a Pull Request



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



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