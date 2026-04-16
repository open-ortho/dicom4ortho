{
  description = "dicom4ortho development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            # Python interpreter — deps are managed by pip/pyproject.toml inside a venv
            pkgs.python310

            # Docker CLI + Compose for integration tests (test/docker-compose.yml)
            pkgs.docker
            pkgs.docker-compose

            # Core build / dev tools
            pkgs.gnumake
            pkgs.git
            pkgs.curl
            pkgs.jq
          ];

          shellHook = ''
            # Expose libstdc++ so pip-installed native wheels (numpy, pillow, etc.) can load.
            # This is a NixOS-specific requirement — the C++ standard library is not in the
            # default linker search path for pip wheel binaries.
            export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:''${LD_LIBRARY_PATH:-}"

            # Create a venv on first use and install the package in editable mode.
            # This keeps Python deps in pyproject.toml as the single source of truth
            # and makes the dicom4ortho / d4o_generate CLI entrypoints available.
            if [ ! -d .venv ]; then
              echo "Creating .venv and installing dicom4ortho[dev] …"
              python3 -m venv .venv
              .venv/bin/pip install --quiet --upgrade pip
              .venv/bin/pip install --quiet -e ".[dev]"
            fi
            source .venv/bin/activate

            echo ""
            echo "dicom4ortho dev shell ready"
            echo "  Python     : $(python --version)"
            echo "  pynetdicom : $(python -c 'import pynetdicom; print(pynetdicom.__version__)')"
            echo "  Docker     : $(docker --version 2>/dev/null || echo 'daemon not running')"
            echo "  Make       : $(make --version | head -1)"
            echo "  CLI        : $(which dicom4ortho)"
            echo ""
            echo "  Note: dicom3tools (dciodvfy) must be installed separately."
            echo "        Run 'make install-dev' for platform-specific instructions."
            echo ""
          '';
        };
      }
    );
}
