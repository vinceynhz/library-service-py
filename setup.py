import setuptools

with open("requirements.txt", "r") as fh:
    requirements = [line.strip() for line in fh]

long_description = """
A REST service to provide data access to resources of a home library (books, magazines, graphic novels, etc).
"""

setuptools.setup(
    name="library-service",
    version="0.0.1",
    author="Vicente Yanez",
    author_email="vince.ynhz@gmail.com",
    description="A Python powered REST service for books and other media library.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=requirements,
)