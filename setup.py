"""Setup configuration for Tian Hanzi Deck"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="tian-hanzi-deck",
    version="2.1.0",
    author="Fenix-Okami",
    description="HSK-based Anki deck generator for learning Chinese characters",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Fenix-Okami/Tian-hanzi-deck",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.11",
    install_requires=[
        "genanki==0.13.1",
        "hanzipy",
        "pandas>=2.0.0",
        "pyarrow>=14.0.0",
        "openai>=1.0.0",
        "strokes",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Topic :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    entry_points={
        "console_scripts": [
            "tian-hanzi=tian_hanzi.cli:main",
        ]
    },
)
