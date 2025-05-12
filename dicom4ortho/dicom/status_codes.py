""" DICOM status codes module.

This module provides dictionaries for DICOM status codes organized by category
and utility functions to work with them.

Return Status 

        status : pydicom.dataset.Dataset
            If the peer timed out, aborted or sent an invalid response then
            returns an empty :class:`~pydicom.dataset.Dataset`. If a valid
            response was received from the peer then returns a
            :class:`~pydicom.dataset.Dataset` containing at least a
            (0000,0900) *Status* element, and, depending on the returned
            value, may optionally contain additional elements (see DICOM
            Standard, Part 7, :dcm:`Annex C<part07/chapter_C.html>`).

            The status for the requested C-STORE operation should be one of the
            following, but as the value depends on the peer SCP this can't be
            assumed:

            *General C-STORE* (DICOM Standard, Part 7, 9.1.1.1.9 and Annex C):

            Success
              | ``0x0000`` - Success

            Failure
              | ``0x0117`` - Invalid SOP instance
              | ``0x0122`` - SOP class not supported
              | ``0x0124`` - Not authorised
              | ``0x0210`` - Duplicate invocation
              | ``0x0211`` - Unrecognised operation
              | ``0x0212`` - Mistyped argument

            *Storage Service* and *Non-Patient Object Storage Service* specific
            (DICOM Standard, Part 4, Annexes B.2.3 and GG):

            Failure
              | ``0xA700`` to ``0xA7FF`` - Out of resources
              | ``0xA900`` to ``0xA9FF`` - Data set does not match SOP class
              | ``0xC000`` to ``0xCFFF`` - Cannot understand

            Warning
              | ``0xB000`` - Coercion of data elements
              | ``0xB006`` - Element discarded
              | ``0xB007`` - Data set does not match SOP class

            *Non-Patient Object Service Class* specific (DICOM Standard, Part
            4, Annex GG.4.2)

            Failure
              | ``0xA700`` - Out of resources
              | ``0xA900`` - Data set does not match SOP class
              | ``0xC000`` - Cannot understand


"""

from pydicom.dataset import Dataset


# Dictionary for general C-STORE status codes
GENERAL_CSTORE_STATUS = {
    0x0000: "Success",
    0x0117: "Invalid SOP instance",
    0x0122: "SOP class not supported",
    0x0124: "Not authorized",
    0x0210: "Duplicate invocation",
    0x0211: "Unrecognized operation",
    0x0212: "Mistyped argument"
}

# Dictionary for Storage Service and Non-Patient Object Storage Service specific status codes
STORAGE_SERVICE_STATUS = {
    # Failure codes
    **{code: "Out of resources" for code in range(0xA700, 0xA800)},
    **{code: "Data set does not match SOP class" for code in range(0xA900, 0xAA00)},
    **{code: "Cannot understand" for code in range(0xC000, 0xD000)},

    # Warning codes
    0xB000: "Coercion of data elements",
    0xB006: "Element discarded",
    0xB007: "Data set does not match SOP class"
}

# Dictionary for Non-Patient Object Service Class specific status codes
NON_PATIENT_OBJECT_STATUS = {
    0xA700: "Out of resources",
    0xA900: "Data set does not match SOP class",
    0xC000: "Cannot understand"
}

# Combined dictionary with all status codes for easy lookup
DIMSE_STATUS_CODES = {
    **GENERAL_CSTORE_STATUS,
    **STORAGE_SERVICE_STATUS,
    **NON_PATIENT_OBJECT_STATUS
}

# Status code classification
STATUS_SUCCESS = 0x0000
STATUS_WARNING_BEGIN = 0xB000
STATUS_WARNING_END = 0xBFFF
STATUS_FAILURE_BEGIN = 0xC000
STATUS_FAILURE_END = 0xFFFF

# Dictionary for status code classification
STATUS_CLASSIFICATION = {
    "SUCCESS": "Success",
    "WARNING": "Warning",
    "FAILURE": "Failure",
    "UNKNOWN": "Unknown"
}


def get_status_meaning(status_code):
    """
    Get the meaning of a DICOM status code.

    Args:
        status_code (int or Dataset): The status code (in hexadecimal) or Dataset with Status attribute

    Returns:
        str: Description of the status code, or "Unknown status code" if not found
    """
    if isinstance(status_code, Dataset) and hasattr(status_code, 'Status'):
        status_code = status_code.Status

    return DIMSE_STATUS_CODES.get(status_code, "Unknown status code")


def get_status_classification(status_code):
    """
    Get the classification of a DICOM status code.

    Args:
        status_code (int or Dataset): The status code (in hexadecimal) or Dataset with Status attribute

    Returns:
        str: Classification of the status code (Success, Warning, Failure, or Unknown)
    """
    if isinstance(status_code, Dataset) and hasattr(status_code, 'Status'):
        status_code = status_code.Status

    if status_code == STATUS_SUCCESS:
        return STATUS_CLASSIFICATION["SUCCESS"]
    elif STATUS_WARNING_BEGIN <= status_code <= STATUS_WARNING_END:
        return STATUS_CLASSIFICATION["WARNING"]
    elif STATUS_FAILURE_BEGIN <= status_code <= STATUS_FAILURE_END:
        return STATUS_CLASSIFICATION["FAILURE"]
    else:
        return STATUS_CLASSIFICATION["UNKNOWN"]


def format_status(status_code):
    """
    Format a status code with its classification and meaning.

    Args:
        status_code (int or Dataset): The status code (in hexadecimal) or Dataset with Status attribute

    Returns:
        str: Formatted status string with code, classification, and meaning
    """
    if isinstance(status_code, Dataset) and hasattr(status_code, 'Status'):
        code_value = status_code.Status
    else:
        code_value = status_code

    classification = get_status_classification(code_value)
    meaning = get_status_meaning(code_value)

    return f"Status: 0x{code_value:04x} ({classification}) - {meaning}"
