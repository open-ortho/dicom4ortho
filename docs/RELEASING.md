# Release checklist: How to release a new version.

1. Check version number and decide what version to release into.
2. Create `release`: e.g. `git flow release start v0.X.0`
3. Bump the version with major, minor or patch and then `bumpversion release` as required. Note: bumpversion commits the version change but does NOT create a git tag — the tag is created by `git flow release finish` in step 11.
4. `make clean`
5. `git merge master`: merge master into here, and fix merge errors.
6. Update release notes in `gh-pages` with major changes of this release. You might want to compare this release branch against master to see logs.
7. Check that README.md is still current.
8. Rebuild the Python environment from scratch to verify no dependency errors:
   - **Nix users:** `nix develop` — the shell hook creates/updates `.venv` and installs `dicom4ortho[dev]` automatically. `dciodvfy` is also provided by the flake; skip step 9.
   - **Non-nix users:** delete and recreate the venv:
     ```
     rm -rf .venv
     python3 -m venv .venv
     source .venv/bin/activate
     pip install -e ".[dev]"
     ```
9. **Non-nix users only:** `make install-dev` — installs `dicom3tools` (`dciodvfy`) required for DICOM validation. On Linux this uses `sudo apt-get install dicom3tools`; on macOS it downloads binaries. Nix users skip this — `dciodvfy` is provided by the flake.
10. `make build`: make sure all tests pass. Build will run lint and tests first.
    - **Nix users:** run inside the dev shell: `nix develop --command make build`
    - **Non-nix users:** `make build` (with `.venv` activated)
11. If all goes well, then merge branch into master: `git flow release finish`. The github actions will take care of deploying to PyPi.
12. Make sure you are on `develop`, then `bumpversion patch` to bump to next `-dev` version.
13. `git push` on master and develop and tags.
14. Update documentation in `gh-pages` branch.

If there is a mistake in the uploaded version, and you need to re-upload, you will have to bump the patch version. PyPi will not allow to re-use the same version number, even if the package has been deleted via the Web GUI.
