# Release checklist: How to release a new version.

1. Check version number and decide what version to release into.
2. Create `release`:  e.g. `git flow release 0.X.0`
3. Bump the version with major, minor or patch and then `bumpversion release` as required.
4. `make clean`
4. `git merge master`: merge master into here, and fix merge errors.
5. Delete pipenv environment and Pipfile.lock and rebuild, to make sure there are no `Pipfile` errors or lock errors.
6. `make install-dev`: make sure `dicom3tools` target works as expected.
5. `make test`: make sure all tests pass.
7. `make build`
8. Make sure proper token for pypi is in `$HOME/.pypirc`. See https://pypi.org/manage/account/token/?selected_project=dicom4ortho
9. `make deploy`
10. If all goes well, then merge branch into master: `git flor release finish`.

If there is a mistake in the uploaded version, and you need to re-upload, you will have to bump the patch version. PyPi will not allow to re-use the same version number, even if the package has been deleted via the Web GUI.