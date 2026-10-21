# Swift release checklist

Do not create a release tag merely because the API compiles. Release work is a
separate maintainer action; this implementation does not publish or retag a release.

- Resolve the root Git-URL package from a clean consumer project at the candidate revision.
- Record Swift/Xcode/SDK versions and the exact dependency graph. Run macOS tests,
  iOS device/simulator builds, and actual simulator tests on a compatible Xcode.
- Run the independent output decoder and IOD validator against exported synthetic
  fixtures, including clinical relationships, and review all warnings and differences.
- Confirm the bundled terminology works offline. Normal package builds/runtime
  do not refresh terminology; `make update_codes` is an explicit maintainer operation
  that renders Python and Swift outputs together. Review generated changes.
- Confirm the capability matrix reflects what was actually qualified. Do not infer
  decoding/preservation support from a UID or an output-encoding test.
- Review dependency/terminology notices and preserve required license/NOTICE files.
- Confirm Python tests, packaging, CLI entry points and publication behavior remain intact.
- After approval, publish a versioned Git tag that includes the root Package.swift.
  Until then, Swift consumers must pin a branch/revision, not an older Python tag.
- If binary dependencies are ever introduced, qualify separate iOS device/simulator
  XCFramework slices before release. No combined arm64 archive is used here.
