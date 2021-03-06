from setuptools import setup, find_packages

with open("README.md", "r") as rm:
    full_description = rm.read()

setup(
    name="StegLibrary",
    version="1.0.1",
    author="Nguyen Thai Binh",
    author_email="binhnt.mdev@gmail.com",
    description="A package implementing and extending on steganography",
    long_description=full_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MunchDev/StegLibrary",
    install_requires=[
        "Pillow",
        "click",
        "pytest",
        "PyQt5",
        "cryptography",
    ],
    packages=find_packages(),
    platforms=["any"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    python_requires=">=3.7",
)
