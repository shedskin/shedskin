import pathlib
import sys

from setuptools import setup

root = pathlib.Path(__file__).parent.resolve()

LONG_DESCRIPTION = (root / "README.rst").read_text(
    encoding="utf-8")

setup(
    name="shedskin",
    version="0.9.8",
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
    install_requires=['conan==1.59.0', 'PyYAML==5.4'] if sys.platform.startswith('win') else [],  # NOTE pyyaml 6.x temp broken with py 3.12
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
            'templates/cpp/*.cpp.tpl',
            'resources/cmake/*.cmake',
            'resources/cmake/*.txt',
            'resources/illegal/illegal.txt',
            'resources/flags/FLAGS*',
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
