from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cip-core",
    version="0.1.0-dev",
    author="Peter Groom",
    author_email="peter@dawnfield.institute",
    description="Cognition Index Protocol implementation for multi-repository automation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dawnfield-institute/cip-core",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "pyyaml>=6.0",
        "jsonschema>=4.0.0",
        "requests>=2.25.0",
        "pathlib>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "pre-commit>=2.0",
        ],
        "mcp": [
            "mcp>=0.1.0",
        ],
        "all": [
            "pytest>=6.0",
            "pytest-cov>=2.0", 
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "pre-commit>=2.0",
            "mcp>=0.1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cip=cip_core.cli.main:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "cip_core": ["schemas/*.yaml", "spec/*.md"],
    },
)
