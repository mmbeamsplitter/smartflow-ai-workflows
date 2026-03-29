"""
Setup script for SmartFlow AI
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="smartflow-ai",
    version="0.1.0",
    author="SmartFlow Team",
    author_email="contact@smartflow.ai",
    description="Universal AI-Powered Workflow Automation Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mmbeamsplitter/smartflow-ai-workflows",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "openai>=1.0.0",
        "anthropic>=0.18.0",
        "requests>=2.31.0",
        "pydantic>=2.0.0",
        "pyyaml>=6.0.0",
        "python-dotenv>=1.0.0",
        "click>=8.1.0",
        "rich>=13.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "black>=23.0.0",
            "mypy>=1.5.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "smartflow=smartflow.cli:cli",
        ],
    },
    include_package_data=True,
    keywords="workflow automation ai llm orchestration",
    project_urls={
        "Bug Reports": "https://github.com/mmbeamsplitter/smartflow-ai-workflows/issues",
        "Source": "https://github.com/mmbeamsplitter/smartflow-ai-workflows",
    },
)