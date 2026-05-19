"""Setup script for EngAI RAG CLI."""

from setuptools import find_packages, setup

setup(
    name="engaichat",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openkb==0.2.0",
        "click==8.4.0",
        "loguru==0.7.3",
        "markitdown==0.1.5",
        "pydantic==2.13.2",
        "fastapi==0.136.1",
        "uvicorn[standard]==0.47.0",
    ],
    entry_points={
        "console_scripts": [
            "engaichat=cli.commands:cli",
        ],
    },
    python_requires=">=3.10",
    description="CLI tool for KfW Energy Consultant Assistant",
)