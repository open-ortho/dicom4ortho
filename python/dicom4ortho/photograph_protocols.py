"""Store photograph prescriptions without overwriting anatomical projection codes.

DENT-OIP #12 and section 3.4.1.3 place view-type codes in Request Attributes /
Scheduled Protocol Code Sequence. These are requests, not proof of acquisition.
Legacy private View Code Sequence entries remain readable, never newly generated.
"""

from copy import deepcopy

from pydicom.dataset import Dataset
from pydicom.sequence import Sequence

from dicom4ortho._generated_codes import IMAGE_TYPES
from dicom4ortho.config import VL_DENTAL_VIEW_CID


_VIEW_SCHEMES = frozenset(item.code.scheme for item in IMAGE_TYPES.values()) | {'99OPOR'}


def is_view_code(code: Dataset) -> bool:
    """Recognize coded identity/context, not meanings or EV/IV-looking free text."""
    identities = [getattr(code, key, '') for key in ('CodeValue', 'LongCodeValue', 'URNCodeValue')]
    if sum(bool(value) for value in identities) != 1 or not getattr(code, 'CodeMeaning', ''):
        return False
    scheme = getattr(code, 'CodingSchemeDesignator', '')
    return scheme in _VIEW_SCHEMES or (
        getattr(code, 'ContextIdentifier', '') == VL_DENTAL_VIEW_CID
        and getattr(code, 'ContextGroupExtensionFlag', '') == 'Y'
    )


def requested_view_codes(dataset: Dataset) -> list[Dataset]:
    """Retain every qualifying request occurrence in its original sequence order."""
    return [code for request in getattr(dataset, 'RequestAttributesSequence', [])
            for code in getattr(request, 'ScheduledProtocolCodeSequence', []) if is_view_code(code)]


def set_view_code(dataset: Dataset, code: Dataset, *, request_index: int | None = None,
                  protocol_index: int | None = None) -> None:
    """Edit one explicit request slot; ambiguous multi-view lists need caller selection.

    Unrelated codes, request identifiers, repeated items and code metadata are preserved.
    The caller's code is copied, and no unrelated CID or default assigning authority is added.
    """
    requests = deepcopy(getattr(dataset, 'RequestAttributesSequence', []))
    if request_index is None:
        if len(requests) > 1:
            raise ValueError('Select request_index when more than one request is present.')
        request_index = 0
    if not requests and request_index == 0:
        requests = [Dataset()]
    if request_index < 0 or request_index >= len(requests):
        raise IndexError('request_index is outside RequestAttributesSequence.')
    request = requests[request_index]
    codes = list(getattr(request, 'ScheduledProtocolCodeSequence', []))
    if protocol_index is None:
        candidates = [index for index, item in enumerate(codes) if is_view_code(item)]
        if len(candidates) > 1:
            raise ValueError('Select protocol_index when more than one view is prescribed.')
        protocol_index = candidates[0] if candidates else len(codes)
    if protocol_index < 0 or protocol_index > len(codes):
        raise IndexError('protocol_index is outside ScheduledProtocolCodeSequence.')
    if protocol_index == len(codes):
        codes.append(deepcopy(code))
    else:
        codes[protocol_index] = deepcopy(code)
    request.ScheduledProtocolCodeSequence = Sequence(codes)
    dataset.RequestAttributesSequence = Sequence(requests)
