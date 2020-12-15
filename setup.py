import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scipp-widgets",  # Replace with your own username
    version="0.0.1",
    author="Matthew Andrew",
    author_email="",
    description="Graphical elements for scipp in notebooks.",
    long_description="",
    long_description_content_type="text/markdown",
    url="https://github.com/scipp/scipp-widgets",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU GENERAL PUBLIC LICENSE",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
