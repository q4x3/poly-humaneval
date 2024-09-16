let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-23.11";
  pkgs = import nixpkgs { config = {}; overlays = []; };
  nixpkgs_old = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-23.05";
  pkgs_old = import nixpkgs_old { config = {}; overlays = []; };
in
pkgs.mkShell.override { stdenv = pkgs.libcxxStdenv; } {
  buildInputs = [
    pkgs.cacert
    pkgs.git

    # C++
    pkgs.gcc13
    pkgs.cmake
    pkgs.ninja
    pkgs.conan

    # C#
    pkgs.dotnet-sdk_8

    # Dart
    pkgs.dart
    
    # Go
    pkgs.go

    # Java
    pkgs.jdk21

    # JavaScript, Typescript 
    pkgs.corepack_21 
    pkgs.nodejs_21
    pkgs.typescript

    # Kotlin
    pkgs.kotlin

    # PHP
    pkgs.php83

    # Python
    pkgs.python3
    pkgs.python311Packages.pip
    pkgs.python311Packages.tqdm
    pkgs.python311Packages.pyyaml
    pkgs.python311Packages.pyparsing
    pkgs.python311Packages.pebble

    # Ruby
    pkgs.ruby_3_2

    # Rust
    pkgs.rustc
    pkgs.cargo

    # Scala
    pkgs.scala_3

    # Swift
    pkgs_old.swift
    pkgs_old.swiftPackages.swiftpm
    pkgs_old.swiftPackages.Foundation

    # TypeScript
    pkgs.typescript
  ];
}