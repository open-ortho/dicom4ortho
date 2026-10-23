"""Public Patient ID assigning-authority authoring, independent of image workflows."""
import re

from pydicom.dataset import Dataset
from pydicom.sequence import Sequence


def _validate_oid(value: str) -> None:
    """Require a canonical numeric OID within DICOM's 64-character UID limit."""
    if not isinstance(value, str) or len(value) > 64 or not re.fullmatch(
        r"(?:0|[1-9][0-9]*)(?:\.(?:0|[1-9][0-9]*))+", value
    ):
        raise ValueError("Assigning-authority OID must be canonical and at most 64 characters")
    components = value.split(".")
    if components[0] not in ("0", "1", "2") or (
        components[0] != "2" and int(components[1]) > 39
    ):
        raise ValueError("Assigning-authority OID has invalid first or second components")


def set_patient_id_assigning_authority(
    dataset: Dataset,
    local_namespace_entity_id: str,
    universal_entity_id_root: str,
    instance_number: int | str,
) -> None:
    """Apply a local issuer and a single ISO universal issuer to ``dataset``.

    ``instance_number`` must be a non-negative integer or ASCII decimal string.
    Leading zeroes in strings are removed to produce a canonical OID component.
    The root and resulting OID must be canonical numeric OIDs of at most 64
    characters. The local label must be non-blank, at most 64 characters (LO),
    without surrounding whitespace, backslashes, or control characters.

    Invalid values raise ValueError before changing the dataset. Existing
    qualifier items are replaced, not appended. PatientID is not modified.
    """
    if not isinstance(local_namespace_entity_id, str) or (
        not local_namespace_entity_id
        or local_namespace_entity_id != local_namespace_entity_id.strip()
        or len(local_namespace_entity_id) > 64
        or re.search(r"[\\\x00-\x1f\x7f]", local_namespace_entity_id)
    ):
        raise ValueError("Local assigning-authority label must be a non-blank single LO value")

    _validate_oid(universal_entity_id_root)
    if isinstance(instance_number, bool) or not isinstance(instance_number, (int, str)):
        raise ValueError("Assigning-authority instance must be a non-negative integer")
    component = str(instance_number)
    if not re.fullmatch(r"[0-9]+", component):
        raise ValueError("Assigning-authority instance must contain only ASCII decimal digits")
    component = component.lstrip("0") or "0"
    universal_entity_id = f"{universal_entity_id_root}.{component}"
    _validate_oid(universal_entity_id)

    qualifier = Dataset()
    qualifier.LocalNamespaceEntityID = local_namespace_entity_id
    qualifier.UniversalEntityID = universal_entity_id
    qualifier.UniversalEntityIDType = "ISO"
    dataset.IssuerOfPatientID = local_namespace_entity_id
    dataset.IssuerOfPatientIDQualifiersSequence = Sequence([qualifier])
