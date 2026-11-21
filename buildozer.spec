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

# Вот эта строчка заставит робота принять лицензии БЕЗ ОШИБОК
android.accept_sdk_license = True

android.api = 33
android.minapi = 21
android.ndk = 23b
android.ndk_api = 21

# Оставляем только 64-битную архитектуру (для современных телефонов)
# Это снизит нагрузку и не даст сборке упасть из-за нехватки памяти
android.archs = arm64-v8a

android.permissions = INTERNET
