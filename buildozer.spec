[app]
# (str) Title of your application
title = Viva AI Gemini
# (str) Package name
package.name = vivagemini
# (str) Package domain
package.domain = ai.viva
# (str) Source code where main.py live
source.dir = .
# (str) Main file of the application
source.main = main.py
# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json,txt
# (str) Version
version = 0.1.0
# (list) Application requirements
requirements = python3,kivy,requests,pyjnius
# (str) Supported orientation
orientation = portrait
# (list) List of service to declare
services =
# (str) Presplash of the application
presplash.filename =
# (str) Icon of the application
icon.filename =
# (str) Supported Android architecture
android.archs = arm64-v8a
# (list) Android permissions
android.permissions = INTERNET,RECORD_AUDIO,CAMERA
# (int) Android API to use
android.api = 34
# (int) Minimum API required
android.minapi = 26
# (str) Android app activity class
android.entrypoint = org.kivy.android.PythonActivity
# (bool) Indicate if the application should be fullscreen
fullscreen = 0

[buildozer]
# (str) Log level
log_level = 2
# (int) Warning when the disk space is low
warn_on_root = 1
# (str) Build directory
build_dir = .buildozer
# (str) Global output directory
bin_dir = bin
