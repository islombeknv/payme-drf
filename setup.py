import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="payme-drf",
    version="0.0.2",
    author="Islombek Normamatov",
    author_email="islomjon2702@gmail.com",
    description="payme-drf",
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.5",
    install_requires=['requests', 'django', 'djangorestframework'],
    url="https://github.com/islombeknv/payme-drf",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ]
)