{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    {
      self,
      nixpkgs,
      flake-utils,
    }:
    flake-utils.lib.eachDefaultSystem (
      system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        # gcloud with extra components baked in
        gcloud = pkgs.google-cloud-sdk.withExtraComponents [
          pkgs.google-cloud-sdk.components.kubectl
          pkgs.google-cloud-sdk.components.gke-gcloud-auth-plugin
        ];
      in
      {
        devShells.default = pkgs.mkShell {
          packages = with pkgs; [
            uv
            python313
            ruff
            pyright

            gcloud
          ];

          env.LD_LIBRARY_PATH =
            with pkgs;
            lib.makeLibraryPath [
              stdenv.cc.cc.lib
              libxcb
              libGL
              glib
            ];
        };
      }
    );
}
