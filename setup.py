from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="gitpulse",
    version="1.0.0",
    author="Your Name",
    description="GitHub Activity Analyzer — beautiful terminal reports for any GitHub user",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gitpulse",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "gitpulse=gitpulse.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Software Development :: Version Control :: Git",
    ],
)
