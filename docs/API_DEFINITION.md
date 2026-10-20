# Native API definition and structural-conformance prototype

**Draft 0.2, 2026-10-20 — issue [#83](https://github.com/open-ortho/dicom4ortho/issues/83).**

| Layer | Source of truth | Purpose |
| --- | --- | --- |
| Functional requirements | [API_CONTRACT.md](API_CONTRACT.md) | Clinical meaning, mutation/ownership and compatibility |
| Logical interface | [dicom4ortho.webidl](../api/dicom4ortho.webidl) | Types, properties, operations, inputs/results, optionality |
| Python binding | [api-bindings.json](../python/api-bindings.json) | Native target/type names and necessary spelling exceptions |
| Implementation tests | Each language's tests | Behavior, integration, DICOM validation |

**A structural pass means declarations exist, not that their bodies work.**
`raise NotImplementedError` is permitted. The conformance checker does not invoke
constructors, getters, setters or operations. Python imports do execute module code.
No Gherkin, shared behavioral harness or generated runtime API is introduced.

## Decision: a bounded Web IDL prototype

[Web IDL](https://webidl.spec.whatwg.org/) is an established interface-definition
language with object interfaces, attributes, constructors, operations, dictionaries,
enums, sequences and nullable types. [WebIDL2](https://github.com/w3c/webidl2.js)
provides the parser; we do not invent another IDL grammar. The Node dependency is
pinned in `tools/api/package-lock.json`; the Python type checker is pinned separately.

This is **not** a claim of a turnkey Web IDL-to-native ecosystem. Web IDL normally
specifies JavaScript/browser bindings. Our small Python emitter and binding rules
are project tooling. We use the syntax/type vocabulary, **not** browser exposure,
JavaScript coercion, DOM exceptions, wire formats or JavaScript ownership semantics.
The parser checks syntax; we do not claim WHATWG Web API semantic validation.

Two project-specific Web IDL extended attributes are deliberately explicit:

- `[External]` names opaque values supplied by the native binding (dataset, image
  bytes, serialized data, date/time), **not** generated generic DICOM wrappers.
- `[StructuralPrototype]` selects the reviewed executable subset. Unmarked draft
  declarations are **not checked**, even if a binding name can be inferred.

Why not the alternatives? UniFFI would introduce a Rust implementation behind
bindings rather than independent ports; WIT would target Wasm components; common
Protobuf/OpenAPI tooling targets messages/services, not this mutable native object
API. We are not adopting those architectural changes just to obtain generators.
Expand the emitter only when a real port needs it; do not build a binding platform.

## Naming and native binding rules

IDL identifiers are logical names, not mandatory literal names in every language.
Python's default is PascalCase types and deterministic snake_case members/parameters;
acronym runs are split as units (`creatorUID` → `creator_uid`). Swift would use its
own lowerCamelCase members/argument labels; Rust its own traits/associated functions,
snake_case operations and native result/error model. Those emitters are **not yet
implemented**. A new port must qualify its rules rather than copy Python's emitter.

Commit only necessary exceptions, not a duplicated complete name map. For example:

| Logical declaration | Python public spelling |
| --- | --- |
| `patientFirstName` | `patient_firstname` (legacy exception) |
| `applyProfile(keyword)` | `set_dicom_attributes_by_type_keyword(type_keyword)` (legacy exception) |
| `getImageTypeCodeDataset(ds)` | `get_image_type_code_dataset(ds)` (automatic) |
| `creatorUid` | `creator_uid` (automatic) |
| `markOriginalImage()` | `is_original_image()` (legacy spelling, actually a mutation) |
| `toByteStream()` | `to_byte()` (legacy result is a stream, not raw bytes) |

Bindings must be reviewed against the specification, not reverse-engineered from
an implementation to make it pass. The prototype rejects unknown binding keys,
unknown member/parameter overrides, name collisions and unmapped selected native
types. Overrides can change identifiers, **not** required types or omit selected
members. Extra native API members remain allowed for compatibility.

The same binding drives scaffold and expected declarations. Bootstrap creates a
new file exclusively; it never overwrites/patches implemented code. Later IDL changes
require regeneration of checks and deliberate implementation edits. Complete mapping
manifests and safe incremental implementation rewriting are intentionally not built.

Do not recase DICOM keywords, UIDs, coded values, schema keys defined by external
standards or arbitrary clinical strings. Python keywords require explicit overrides.
More complex native naming rules are future emitter work, not silently guessed exceptions.

## Type, omission and error boundaries

- `DOMString` maps to Python `str`, `boolean` to `bool`, `undefined` result to `None`.
  The prototype maps `NativeDataset` directly to `pydicom.dataset.Dataset`.
- `T?` permits explicit `None`; `optional` permits omission. They are different.
  Selected optional arguments specify a `null` default, mapped to `None`.
  Python's nullable type-code setter already treats `None` as a no-op, not removal.
- Optional dictionary members may be absent. A nullable member may explicitly be
  null; an empty string is still a supplied string, not automatically absence.
  Constructors may have documented compatibility normalization.
- `PhotographOptions` maps to Python's existing `**metadata`, using existing keyword
  names; it does not force a new runtime options class. The dictionary intentionally
  excludes legacy day-offset aliases from the new core, not from Python support.
- Calendar dates are native date-without-time values; timestamps retain their native
  offset/time semantics. Python keeps its additional datetime/ISO-string inputs;
  other ports need not reproduce these historical convenience formats. No implicit
  instant-to-calendar-date timezone conversion.
- `EncodedImage` is encoded input bytes, not decoded pixels. `SerializedDicom` maps
  to Python's existing rewound `io.BytesIO`, Swift may use `Data`. No common byte ABI.
- Group collection projections preserve child handles. A binding can return a
  collection view/copy without cloning the child records. Python retains `Photos`,
  `Series`, `UID`, `StudyUID`, `__iter__` and `__len__`; the prototype does not yet
  generate their native projection checks.
- Errors use the native language. Python permits exceptions, including
  `NotImplementedError`. A future Swift profile must spell out `throws`/mutating and
  identity semantics; a Rust profile must specify `Result` and borrowing. Web IDL
  alone does not settle those choices. They need reviewed binding definitions and
  native compile probes before claiming those ports conform.

## Run the prototype

From the repository root with Python 3.10+ and Node 22+:

```sh
python -m venv .venv
. .venv/bin/activate
pip install -e '.[dev]'
pip install -r tools/api/requirements.txt
npm ci --prefix tools/api --ignore-scripts
make api-check-pilot PYTHON=python
make api-test PYTHON=python
```

Bootstrap an **unimplemented Python prototype** in a new file:

```sh
node tools/api/generate.mjs --scaffold /tmp/PhotographSkeleton.py
```

It uses the committed Python binding; it does not import or rewrite production
classes. Generation can also write `contract.py` (a `typing.Protocol`), `probe.py`
(an assignment of the actual native type to that protocol plus compile-only
keyword-call probes), and `surface.json`
(annotation/default audit metadata) into a **new** `--output DIRECTORY`. These are
temporary test artifacts, not new maintained specification files or installed stubs.

Mypy checks actual `.py` declarations through the current worktree's source path,
not generated replacement `.pyi` files or another checkout's editable installation.
The small reflection precheck rejects missing/`Any` annotations, missing accessors,
wrong staticness and changed selected null defaults. Mypy checks property types,
writability and callable signatures. Explicit keyword-call probes check argument
names too: protocol assignment alone did not reject a renamed argument in the
negative tests. No probe is executed.
Compatible broader signatures are allowed; this is structural substitutability,
not a ban on additional native convenience parameters or methods.

Mypy does not prove runtime types or behavior, and accurate annotations do not
prove implementation bodies. Mutations test that a correctly typed unimplemented
class passes while a missing method, wrong name/parameter/type/nullability, missing
setter, incorrect staticness/default or unverified annotation fails. Reflection
is not a general Python runtime API inspector or a replacement type checker.

## Coverage and one-PR boundary

The pilot covers **15 members** of `OrthodonticPhotograph`: patient/provider/operator
name components, type-code property/static helpers, profile/direction operations,
extra-/intraoral classification, live dataset access and preparation. Python changes
are annotations only. No new wrappers or warnings are needed because no names change.

The remaining interface, constructor/options flattening, group projections, native
date/time/serialization types, dictionaries/enums and `ViewTypeReport` extraction
are **reviewable definitions, not qualified generated/checkable bindings**. The tool
prints selected/total interface coverage and never reports full API conformance.
It fails rather than ignoring an unsupported **selected** construct. The extraction
namespace specifies a new additive capability; Python's first-result helper is not
misrepresented as its implementation.

This PR does not finish extraction, Swift materialization, Rust scaffolding or codec
qualification. Before expanding the prototype, review the complete native bindings
and decide whether the bounded Web IDL approach remains cheaper than maintaining
native declaration contracts. Language tests remain independent throughout.

Review points before promoting unmarked definitions to required checks include
constructor keyword flattening, native date/time getter-versus-setter types, and
whether to add a typed image-attachment operation rather than standardize Python's
retained-source `set_image()` result (`False` for no input, otherwise `None`). The
prototype does not force those legacy shapes on future ports or conceal the gaps.
In particular, Python's constructor currently parses birthdate from a string; the
draft's typed calendar-date option would need narrowly additive date acceptance
before qualifying that constructor binding. Existing ISO-string callers must keep
working. This normalization is not part of the annotated prototype.

## Local qualification (2026-10-20)

Python 3.10.16, pydicom 2.4.5, pynetdicom 2.1.0; Node 22.23.3,
WebIDL2 24.5.0 and mypy 2.4.0:

- 27 structural-tool tests pass, including deliberate declaration mutations.
- 132 non-E2E Python tests run with 4 skips, no failures.
- Error-only lint and wheel/source builds pass. The source archive independently
  passes the structural pilot, all 27 tool tests and the 3 new compatibility tests.
- AST comparison confirms production source edits change annotations only.
  The wheel contains no generator/IDL runtime dependency.

Orthanc/network tests and Swift/Rust compiler checks were not run; those ports are
not introduced here. Local success is not a claim that GitHub Actions has run.
