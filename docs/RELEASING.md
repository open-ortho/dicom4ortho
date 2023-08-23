# Release checklist: How to release a new version.

1. Check version number and decide what version to release into.
2. Create `release`:  e.g. `git flow release 0.X.0`
3. Bump the version with major, minor or patch and then `bumpversion release` as required.
4. `make test`: make sure all tests pass.
5. `make install-dev`: make sure `dicom3tools` target works as expected.
6. `make build`
7. Make sure proper token for pypi is in `$HOME/.pypirc`. See https://pypi.org/manage/account/token/?selected_project=dicom4ortho
8. `make deploy`
9. If all goes well, then merge branch into master: `git flor release finish`.