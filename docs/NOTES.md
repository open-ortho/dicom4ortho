
## Feature Roadmap

### v0

* Load single PNG/JPG file
* Manually set metadata from filename, or hard code

### v1

* Load entire directory, for batch conversion
* Load metadata from filename, like the files of the linedrawings, using our abbreviations.

## Resources

* [Instructions for creating a DICOM object from scratch in DICOM](https://pydicom.github.io/pydicom/dev/auto_examples/input_output/plot_write_dicom.html#sphx-glr-auto-examples-input-output-plot-write-dicom-py)
* [Writing DICOM Files](https://pydicom.github.io/pydicom/dev/old/writing_files.html)

Required for testing currently:
[dicom3tools](https://www.dclunie.com/dicom3tools.html), in particular
dciodvfy binary.

## UIDs

Dicom uses a bunch of UIDs for things.

### SOP Class UIDs 

This basically defined the IOD. So in our case it's static, and it defines VL Image IOD

* Part 4 B.5

### Instance UID

This is a different unique ID for each image. Needs to be freshly generated.

* Part 5 B.2 to specify how to generate

### Implementation Class UID

Basically, this a unique ID for the software. Probably want a different one
for each version.

Different equipment of the same type or product line (but having different
serial numbers) shall use the same Implementation Class UID if they share the
same implementation environment (i.e., software).

* Part 7 D.3.3.2

### StudyInstanceUID

### SeriesInstanceUID


Version v0.1.0-dev
