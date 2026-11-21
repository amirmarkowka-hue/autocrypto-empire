[app]
title = AutoCrypto Empire
package.name = autocryptoempire
package.domain = org.dmitry
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# Важно: указываем pyjnius для работы с Android API
requirements = python3,kivy,pyjnius

orientation = portrait
fullscreen = 0

# --- Критически важные настройки для Android ---
android.accept_sdk_license = True
android.skip_update = False
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a, armeabi-v7a
android.permissions = INTERNET

# Фиксируем версии инструментов для стабильности
android.sdk = 24
android.buildtools = 30.0.3
