import pywup.consts as c

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name=c.name,
    version=c.version,
    author=c.author,
    author_email=c.author_email,
    description=c.description,
    long_description=long_description,
    long_description_content_type="text/markdown",
        url="https://github.com/diegofps/pywup",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        'console_scripts': [
            'wup = pywup.wup:wup'
        ],
    },
    install_requires=[
        'colorcet', 'tqdm', 'PyYAML'
    ],
    extras_require={
        "full": ['numpy', 'matplotlib']
    }
)
