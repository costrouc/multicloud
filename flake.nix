{
  description = "magix-k8s";

  inputs = {
    nixpkgs = { url = "github:nixos/nixpkgs/nixpkgs-unstable"; };
  };

  outputs = inputs@{ self, nixpkgs, ... }:
    let
      pkgs = import nixpkgs { system = "x86_64-linux"; };

      pythonPackages = pkgs.python3Packages;
    in {
      packages.x86_64-linux.default = pythonPackages.buildPythonPackage {
        pname = "magix-k8s";
        version = "latest";
        format = "pyproject";

        src = ./.;

        buildInputs = [
          pythonPackages.setuptools
        ];

        propagatedBuildInputs = [
          pythonPackages.ruamel-yaml
          pythonPackages.pytesseract
        ];
      };

      apps.x86_64-linux.default = {
        type = "app";
        program = "${self.packages.x86_64-linux.default}/bin/magix-k8s";
      };

      devShell.x86_64-linux = pkgs.mkShell {
        buildInputs = [
          pythonPackages.questionary
        ];
      };
    };
}