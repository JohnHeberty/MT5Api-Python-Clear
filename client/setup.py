# MT5 Trading Client - Arquivo de setup para distribuição
from setuptools import setup, find_packages

# Ler descrição do README
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "Cliente Python para MT5 Trading API com Clean Architecture"

setup(
    name="mt5-trading-client",
    version="1.0.0",
    author="MT5 Trading API Client",
    author_email="",
    description="Cliente Python para MT5 Trading API com Clean Architecture",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Financial :: Investment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
        "numpy>=1.21.0",
        "python-dotenv>=0.19.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "mt5-client=mt5_client.cli:main",
        ],
    },
    keywords="mt5 metatrader trading api client finance forex",
    project_urls={
        "Bug Reports": "",
        "Source": "",
        "Documentation": "",
    },
)