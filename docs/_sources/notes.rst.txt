DICOM UIDs
==========

Dicom requires unique identifiers for in various locations. This section
summarizes the ones used here.

SOP Class UIDs
~~~~~~~~~~~~~~

This identifies the IOD, which in our case is static, and should
be the UID of the VL Image IOD.

-  Part 4 B.5

Instance UID
~~~~~~~~~~~~

A different unique ID for each image. Needs to be freshly generated.

-  Part 5 B.2 specifies how to generate

Implementation Class UID
~~~~~~~~~~~~~~~~~~~~~~~~

A unique ID for the software. DICOM probably requires a different one for each
version of the software.

_Different equipment of the same type or product line (but having
different serial numbers) shall use the same Implementation Class UID if
they share the same implementation environment (i.e., software)._

-  Part 7 D.3.3.2

StudyInstanceUID
~~~~~~~~~~~~~~~~

TODO

SeriesInstanceUID
~~~~~~~~~~~~~~~~~

TODO