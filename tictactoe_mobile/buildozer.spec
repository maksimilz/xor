[app]
title = Крестики-Нолики
package.name = tictactoe
package.domain = org.example

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 1.0

requirements = python3,kivy

orientation = portrait

android.permissions = INTERNET
android.api = 31
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.gradle_dependencies = org.jetbrains.kotlin:kotlin-stdlib-jdk7:1.7.0

[buildozer]
log_level = 2
warn_on_root = 1 