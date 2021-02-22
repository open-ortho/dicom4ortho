""" Add DICOM Attributes not yet part of DICOM

    This is from CP-1570, and should be removed once the CP becomes part of
    the main standard. Note that tags may differ.
"""
from pydicom.datadict import DicomDictionary, keyword_dict


# Define items as (VR, VM, description, is_retired flag, keyword)
#   Leave is_retired flag blank.
dental_acquisition_context = {
    0x10011001: ('SQ', '1', "Acquisition View", '', 'AcquisitionView'),
    0x10011002: ('SQ', '1', "Image View", '', 'ImageView'),
    0x10011003: ('SQ', '1', "Functional condition present during"
                 "acquisition", '', 'FunctionalCondition'),
    0x10011004: ('SQ', '1', "Occlusal Relationship", '', 'OcclusalRelationship'),
}

# Update the dictionary itself
DicomDictionary.update(dental_acquisition_context)

# Update the reverse mapping from name to tag
keyword_dict.update(dict([(val[4], tag) for tag, val in
                          dental_acquisition_context.items()]))
