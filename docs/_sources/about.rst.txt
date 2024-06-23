About The Project
=================

The DICOM standard is ready for any developer in the orthodontic
community to implement. However, it can be complicated and implementation can be
time consuming. The DICOM standard is also does not contain an explicit
explanation on orthodntic photographs, allowing the developer too much freedom.

This is why we decided to implement ANSI Standard ADA-1107, which defines
exactly how to use DICOM to encode orthodontic photographs.

We want to create a proof of concept to demonstrate how to properly store
orthodontic visible light images (aka photographs) using DICOM, while ensuring
all codes (necessary to uniquely identify each image type) are in the proper
place.

Here’s why:

-  Your time should be focused on creating something amazing.
-  Being able to import and export DICOM images to and from your
   orthodontic software will open doors to you and the orthodontic
   provider.
-  No one software will serve all orthodontic providers completely.
   Adding interoperability will allow your product to integrate with
   others, giving additional value to your solution.

You may suggest changes by forking this repo and creating a pull request
or opening an issue. Thanks to all the people have have contributed to
this project!

A list of commonly used resources that we find helpful are listed in the
acknowledgements.

Built With
----------

-  `pydicom <https://pydicom.github.io/>`__
-  `pillow <https://python-pillow.org/>`__
-  `dicom3tools <https://www.dclunie.com/dicom3tools.html>`__

Contributing
------------

Contributions are what make the open source community such an amazing
place to be learn, inspire, and create. Any contributions you make are
**greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch
   (``git checkout -b feature/AmazingFeature``)
3. Commit your Changes (``git commit -m 'Add some AmazingFeature'``)
4. Push to the Branch (``git push origin feature/AmazingFeature``)
5. Open a `Pull
   Request <https://docs.github.com/en/github/collaborating-with-issues-and-pull-requests/creating-a-pull-request>`__

License
-------

Distributed under the MIT License. See `LICENSE <LICENSE>`__ for more
information.

Contact
-------

Toni Magni- [@zgypa](https://twitter.com/zgypa) - open-ortho@afm.co

Project Link: https://open-ortho.github.io

Resources
---------

-  `Instructions for creating a DICOM object from scratch in
   DICOM <https://pydicom.github.io/pydicom/dev/auto_examples/input_output/plot_write_dicom.html#sphx-glr-auto-examples-input-output-plot-write-dicom-py>`__
-  `Writing DICOM
   Files <https://pydicom.github.io/pydicom/dev/old/writing_files.html>`__

Required for testing currently: `dicom3tools
<https://www.dclunie.com/dicom3tools.html>`__, in particular dciodvfy binary.

Acknowledgements
----------------

-  `DICOM <https://www.webpagefx.com/tools/emoji-cheat-sheet>`__
-  `American Dental Association Standards Committee for Dental
   Informatics <https://www.ada.org/en/science-research/dental-standards/standards-committee-on-dental-informatics>`__

