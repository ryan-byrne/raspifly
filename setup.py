from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="raspifly",
    version="0.0.1",
    author="Ryan Byrne",
    author_email="ryan@byrne.es",
    description="Rasplify is an Open Source Drone Using Raspberry Pi and Arduino",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ryan-byrne/raspifly",
    entry_points={
        "console_scripts":['raspifly-server=raspifly.scripts:raspifly_server']
    },
    install_requires=[
        'flask',
        'pyserial'
    ],
    project_urls={
        "Bug Tracker": "https://github.com/pypa/sampleproject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
)