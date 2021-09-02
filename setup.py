import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="FTIR-background-subtract",
    version="1.2.0",
    author="Kayla Iacovino and Nial",
    author_email="kaylaiacovino@gmail.com",
    description=("A GUI tool for drawing polynomial backgrounds on FTIR spectra and subtracting "
                 "them to get total absorbance (by height) of a desired peak."),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kaylai/ftir-background-subtract",
    packages=setuptools.find_packages(),
    install_requires=[
            'numpy',
            'matplotlib',
            'wxPython'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
