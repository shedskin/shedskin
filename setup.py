from setuptools import setup, Command
import pathlib

root = pathlib.Path(__file__).parent.resolve()

LONG_DESCRIPTION = (root / "README.rst").read_text(
    encoding="utf-8")

setup(
    name="shedskin",
    version="0.9.6",
    description="Shed Skin is a restricted-Python-to-C++ compiler.",
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    url="https://shedskin.github.io/",
    author="Mark Dufour and contributors",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Compilers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
    ],
    keywords="compiler, translator, cpp, extension",
    packages=['shedskin'],
    python_requires=">=3.8, <4",
    install_requires=[],
    extras_require={
        # "dev": ["check-manifest"],
        "test": ["pytest", "tox"],
    },
    package_data={
        'shedskin': [
            'lib/*.cpp', 
            'lib/*.hpp',
            'lib/builtin/*.cpp',
            'lib/builtin/*.hpp',
            'lib/*.py',
            'lib/os/*.cpp',
            'lib/os/*.hpp',
            'lib/os/*.py',
            'FLAGS*',
            'illegal',
            'templates/cpp/*.cpp.tpl',
            'resources/cmake/modular/*.cmake',
            'resources/cmake/modular/*.txt',
            'resources/cmake/single/*.txt',
            'resources/illegal/illegal.txt',
            'resources/conan/*.txt',
        ]
    },
    entry_points={
        "console_scripts": [
            "shedskin=shedskin.__main__:run",
        ],
    },
    project_urls={
        "Homepage": "https://shedskin.github.io",
        "Bug Reports": "https://github.com/shedskin/shedskin/issues",
        "Source": "https://github.com/shedskin/shedskin",
        "Documentation": "https://shedskin.readthedocs.io",
    },
)
