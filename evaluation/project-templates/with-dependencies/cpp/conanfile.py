from conan import ConanFile
from conan.tools.cmake import CMakeToolchain, CMakeDeps, CMake


class MyConan(ConanFile):
    name = "myconan"
    version = "0.1"

    requires = "openssl/3.1.2"
    settings = "os", "compiler", "build_type", "arch"
    exports_sources = "CMakeLists.txt", "src/*"

    def generate(self):
        if self.settings.os == "Windows":
            tc = CMakeToolchain(self)
        else:
            tc = CMakeToolchain(self, generator="Ninja")
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        self.copy("*.exe", dst="")
