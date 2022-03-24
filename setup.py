import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="WARIO Editor",
    version="1.0.1",
    author="Thomas Mudway, Oliver Cook, Ron Harwood",
    description="Pipeline editor and front end for WARIO",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/McMasterRS/WARIO-Editor",
    packages=setuptools.find_packages(),
    package_data={
        "":["*.json", "*.ui"],
    },
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'PyQt5',
        'PyQtWebEngine',
        'blinker',
        'graphviz',
        'wario'
    ],
    python_requires='>=3.6',
)