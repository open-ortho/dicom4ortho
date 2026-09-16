# Bulk conversion example

After installing `dicom4ortho`, run the example from the repository root:

```bash
dicom4ortho examples/input_from.csv
```

Image paths in `input_from.csv` are resolved relative to the CSV file. The
command writes three DICOM files into this directory; generated `*.dcm` files
are ignored by Git.

Run `dicom4ortho list-image-types` to list all supported image types.
