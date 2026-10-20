// Draft 0.2 — native-library interface vocabulary, not a JavaScript/Web API.
// Clinical/ownership rules: docs/API_CONTRACT.md. Binding rules: docs/API_DEFINITION.md.
// StructuralPrototype marks the deliberately small executable subset in issue #83.

// External native values. These are NOT generated DICOM/date/byte wrapper classes.
[External] interface NativeDataset {};
[External] interface EncodedImage {};
[External] interface SerializedDicom {};
[External] interface CalendarDate {};
[External] interface Timestamp {};

dictionary PhotographOptions {
  DOMString inputImageFilename;
  EncodedImage inputImageBytes;
  DOMString outputImageFilename;
  NativeDataset dicomMwl;
  DOMString imageType;
  DOMString viewCodeKeyword;
  DOMString patientFirstName;
  DOMString patientLastName;
  DOMString patientId;
  DOMString patientSex;
  CalendarDate patientBirthdate;
  DOMString dentalProviderFirstName;
  DOMString dentalProviderLastName;
  DOMString operatorFirstName;
  DOMString operatorLastName;
  DOMString manufacturer;
  DOMString studyInstanceUid;
  DOMString seriesInstanceUid;
  DOMString sopInstanceUid;
  DOMString studyDescription;
  DOMString seriesDescription;
  Timestamp acquisitionDatetime;
  DOMString treatmentEventType;
  CalendarDate treatmentEventDate;
  DOMString burnedInAnnotation = "NO";
};

interface OrthodonticPhotograph {
  constructor(optional PhotographOptions options = {});

  [StructuralPrototype] attribute DOMString patientFirstName;
  [StructuralPrototype] attribute DOMString patientLastName;
  [StructuralPrototype] attribute DOMString dentalProviderFirstName;
  [StructuralPrototype] attribute DOMString dentalProviderLastName;
  [StructuralPrototype] attribute DOMString operatorFirstName;
  [StructuralPrototype] attribute DOMString operatorLastName;
  attribute DOMString patientId;
  attribute DOMString patientSex;
  attribute CalendarDate patientBirthdate;
  attribute DOMString? studyInstanceUid;
  attribute DOMString? seriesInstanceUid;
  attribute DOMString? studyDescription;
  attribute DOMString? seriesDescription;
  attribute DOMString? equipmentManufacturer;
  attribute DOMString? inputImageFilename;
  attribute EncodedImage? inputImageBytes;
  attribute DOMString? outputImageFilename;

  [StructuralPrototype] attribute NativeDataset? imageTypeCodeDataset;
  [StructuralPrototype] static NativeDataset? getImageTypeCodeDataset(NativeDataset ds);
  [StructuralPrototype] static undefined setImageTypeCodeDataset(
    NativeDataset ds, NativeDataset? codeDataset, optional DOMString? creatorUid = null);
  [StructuralPrototype] undefined applyProfile(optional DOMString? keyword = null);
  [StructuralPrototype] undefined setViewCode(DOMString keyword);
  [StructuralPrototype] boolean isExtraoral();
  [StructuralPrototype] boolean isIntraoral();

  undefined setTreatmentProgressFromDate(
    DOMString eventType, CalendarDate eventDate, optional CalendarDate? acquisitionDate = null);
  undefined setTimeCaptured(Timestamp timeCaptured);
  undefined copyMwlTags(optional NativeDataset? dicomMwl = null);

  // Uses retained input filename/bytes in Python; False means absent input.
  (boolean or undefined) setImage();
  undefined setExifTags();
  undefined markDigitizedImage();
  undefined markPrimaryImage();
  undefined markOriginalImage();
  undefined markDerivedImage();
  undefined setLossyCompression(boolean lossy);

  [StructuralPrototype] NativeDataset toDataset();
  [StructuralPrototype] undefined prepare();
  SerializedDicom toByteStream();
  undefined save(optional DOMString? filename = null);
  undefined load(DOMString filename);
};

dictionary GroupOptions {
  DOMString uid;
  DOMString description;
};

interface OrthodonticSeries {
  constructor(optional GroupOptions options = {});
  attribute DOMString uid;
  attribute DOMString? studyUid;
  attribute DOMString? description;
  // A collection projection; logical child records remain shared, not snapshots.
  readonly attribute FrozenArray<OrthodonticPhotograph> photographs;
  undefined add(OrthodonticPhotograph photo);
  undefined save(optional DOMString? filenamePrefix = null);
};

interface OrthodonticStudy {
  constructor(optional GroupOptions options = {});
  attribute DOMString uid;
  readonly attribute FrozenArray<OrthodonticSeries> series;
  undefined add(OrthodonticSeries series);
  undefined save();
};

// New additive extraction contract. Not an alias for the existing first-code getter.
enum DeclarationRole { "image-instance", "scheduled-protocol", "copied-scheduled-protocol" };
enum RecognitionStatus { "recognized", "unresolved", "unrelated", "malformed" };
enum CodeRepresentation { "short", "long", "urn", "missing", "ambiguous" };
enum DiagnosticSeverity { "info", "warning", "error" };

dictionary CodedIdentity {
  required CodeRepresentation representation;
  DOMString? codeValue = null;
  DOMString? longCodeValue = null;
  DOMString? urnCodeValue = null;
  DOMString? scheme = null;
  DOMString? schemeVersion = null;
  DOMString? meaning = null;
  DOMString? contextIdentifier = null;
  DOMString? contextUid = null;
  DOMString? contextGroupVersion = null;
  DOMString? extensionFlag = null;
  DOMString? localVersion = null;
  DOMString? extensionCreatorUid = null;
};

dictionary SourcePathItem {
  required DOMString sequenceKeyword;
  required unsigned long itemIndex; // Zero-based index in this contract.
};

dictionary DeclarationSource {
  required sequence<SourcePathItem> path;
  DOMString? scheduledProcedureStepId = null;
  DOMString? requestedProcedureId = null;
};

dictionary ViewTypeEntry {
  required CodedIdentity code;
  required DeclarationRole role;
  required DeclarationSource source;
  required RecognitionStatus status;
  DOMString? resolvedKeyword = null;
};

dictionary ViewTypeDiagnostic {
  required DiagnosticSeverity severity;
  required DOMString code;
  required DOMString message;
  DeclarationSource? source = null;
};

dictionary ViewTypeReport {
  // Recognized/unresolved types, including malformed qualifying candidates.
  required sequence<ViewTypeEntry> declarations;
  // Unrelated codes and malformed entries that cannot qualify as type candidates.
  required sequence<ViewTypeEntry> otherEntries;
  required sequence<ViewTypeDiagnostic> diagnostics;
  required sequence<DOMString> unsupportedContexts;
};

namespace ViewTypes {
  ViewTypeReport extractDeclaredViewTypes(NativeDataset dataset);
};
