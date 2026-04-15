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

        # nixpkgs ships pynetdicom 3.x, but pyproject.toml requires >=2,<3.
        # Build 2.1.1 from PyPI source.
        pynetdicom2 = pkgs.python310Packages.buildPythonPackage rec {
          pname = "pynetdicom";
          version = "2.1.1";
          format = "pyproject";
          src = pkgs.fetchPypi {
            inherit pname version;
            # sha256 from: nix-prefetch-url --unpack
            # https://files.pythonhosted.org/packages/source/p/pynetdicom/pynetdicom-2.1.1.tar.gz
            sha256 = "sha256-lnH7ru/X7WSRuxKOBW1YhihytLIzXUu+RLvakZjNv+o=";
          };
          nativeBuildInputs = with pkgs.python310Packages; [ poetry-core ];
          propagatedBuildInputs = with pkgs.python310Packages; [ pydicom ];
          doCheck = false;
        };

        python = pkgs.python310.withPackages (ps: with ps; [
          # Runtime dependencies (pyproject.toml [dependencies])
          pynetdicom2
          ps.pydicom
          ps.pillow
          ps.prettytable
          ps.numpy
          ps.urllib3
          ps.requests

          # Build system
          ps.setuptools
          ps.wheel

          # Dev dependencies (pyproject.toml [dev])
          ps.wrapt
          ps.pylint
          ps.twine
          ps.autopep8
          ps.pytest
          ps.build
          ps.bump2version
        ]);
      in
      {
        devShells.default = pkgs.mkShell {
          packages = [
            python

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
            # Make the package importable directly from source (editable-install equivalent).
            # All heavy deps are already in the Nix Python environment above.
            export PYTHONPATH="$PWD:''${PYTHONPATH:-}"

            echo ""
            echo "dicom4ortho dev shell ready"
            echo "  Python     : $(python --version)"
            echo "  pynetdicom : $(python -c 'import pynetdicom; print(pynetdicom.__version__)')"
            echo "  Docker     : $(docker --version 2>/dev/null || echo 'daemon not running')"
            echo "  Make       : $(make --version | head -1)"
            echo ""
          '';
        };
      }
    );
}
