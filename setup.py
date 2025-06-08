from cx_Freeze import setup, Executable
import sys

base = None
if sys.platform == "win32":
    base = "Win32GUI"

executables = [
    Executable("main.py", base=base)
]

build_exe_options = {
    "packages": ["pygame", "pyttsx3", "speech_recognition", "aifc"],
    "include_files": [
        "assets/", "recursos/", "log.dat"
    ],
    "includes": ["chunk", "audioop"]
}

setup(
    name="MidNightRunner",
    version="1.0",
    description="Jogo desenvolvido em Python com Pygame",
    options={"build_exe": build_exe_options},
    executables=executables
)