# Release checklist: How to release a new version.

1. Check version number and decide what version to release into.
2. Create `release`:  e.g. `git flow release start 0.X.0`
3. Bump the version with major, minor or patch and then `bumpversion release` as required.
4. `make clean`
4. `git merge master`: merge master into here, and fix merge errors.
5. Update release notes in `gh-pages` with major changes of this release. You might want to compare this release branch agains master to see logs.
6. Check that README.md is still current.
5. `pipenv --rm` Delete pipenv environment
6. `rm Pipfile.lock` 
7. `pipenv install --dev` rebuild, to make sure there are no `Pipfile` errors or lock errors.
8. `make install-dev`: make sure `dicom3tools` target works as expected.
9. `make build`: make sure all tests pass. Build will run test first.
11. If all goes well, then merge branch into master: `git flow release finish`. The github actions will take care of deploying to PyPi.
12. Make sure you are on `develop`, then `bumpversion patch` to bump to next `-dev` version.
13. Update documentation in `gh-pages` branch.

If there is a mistake in the uploaded version, and you need to re-upload, you will have to bump the patch version. PyPi will not allow to re-use the same version number, even if the package has been deleted via the Web GUI.