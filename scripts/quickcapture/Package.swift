// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "QuickCapture",
    platforms: [.macOS(.v13)],
    targets: [
        .executableTarget(
            name: "QuickCapture",
            path: "Sources/QuickCapture",
            linkerSettings: [
                .linkedFramework("Cocoa"),
                .linkedFramework("Carbon")
            ]
        )
    ]
)
