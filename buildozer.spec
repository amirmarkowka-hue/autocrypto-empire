[app]
title = AutoCrypto Empire
package.name = autocryptoempire
package.domain = org.dmitry
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3,kivy==2.2.1,pyjnius,cython==0.29.36

orientation = portrait
fullscreen = 0

android.accept_sdk_license = True
android.skip_update = False

android.api = 33
android.minapi = 21
android.ndk = 21e
android.ndk_api = 21

android.archs = arm64-v8a

android.permissions = INTERNET
