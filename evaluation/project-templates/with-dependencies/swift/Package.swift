// swift-tools-version: 5.8
// The swift-tools-version declares the minimum version of Swift required to build this package.
import Foundation
import PackageDescription

let package = Package(
  name: "main",
  dependencies: [
    .package(url: "https://github.com/krzyzanowskim/CryptoSwift.git", branch: "main")
  ],
  targets: [
    // Targets are the basic building blocks of a package, defining a module or a test suite.
    // Targets can depend on other targets in this package and products from dependencies.
    .executableTarget(
      name: "main",
      dependencies: [
        .product(name: "CryptoSwift", package: "CryptoSwift")
      ],
      path: "src")
  ]
)