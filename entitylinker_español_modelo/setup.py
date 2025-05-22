from setuptools import setup, find_packages

setup(
    name="tfg_entitylinker",
    version="1.0",
    author="Antonio Perea",
    description="Sistema de Entity Linking en español con Wikidata",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "spacy",
        "requests",
        "sentence-transformers",
        "scikit-learn",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    include_package_data=True,
)
