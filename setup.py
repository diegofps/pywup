import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pywup",
    version="0.0.3",
    author="Diego Souza",
    author_email="contact@wespa.com.br",
    description="A small set of tools",
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
        'console_scripts': ['wup1=pywup.cmdline:py_wup', 'wup2=pywup.cmdline:py_wup_2'],
    }
)
