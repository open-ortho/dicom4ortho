#!/usr/bin/env bash
# Extracts the qualified signed toolchain on an ephemeral GitHub runner only.
# Does not run an installer, change xcode-select, or modify a workstation toolchain.
set -euo pipefail

: "${RUNNER_TEMP:?This script is for an ephemeral CI runner}"
: "${GITHUB_PATH:?GitHub Actions PATH output is required}"
package="$RUNNER_TEMP/swift-6.4.1-RELEASE-osx.pkg"
expanded="$RUNNER_TEMP/dicom4ortho-swift-6.4.1"
url=https://download.swift.org/swift-6.4.1-release/xcode/swift-6.4.1-RELEASE/swift-6.4.1-RELEASE-osx.pkg

curl --fail --silent --show-error --location --retry 3 "$url" --output "$package"
# Observed SHA-256 of the Apple-trusted signed package independently qualified on
# mainframe1. A mismatch must fail, not silently accept a changed download.
printf '%s  %s\n' c34e7e5fb0be4bcd61decfd40db1766434d8952d68e37aed90bcff4e8547951c "$package" | shasum -a 256 --check
pkgutil --check-signature "$package" | tee "$RUNNER_TEMP/swift-package-signature.txt"
grep -F 'Swift Open Source (V9AUD2URP3)' "$RUNNER_TEMP/swift-package-signature.txt"
pkgutil --expand-full "$package" "$expanded"
toolchain="$expanded/swift-6.4.1-RELEASE-osx-package.pkg/Payload/usr/bin"
"$toolchain/swift" --version
printf '%s\n' "$toolchain" >> "$GITHUB_PATH"
# Remove only the exact archive downloaded by this script after verified expansion.
rm "$package"
