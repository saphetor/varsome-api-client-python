import sys
from os import path

from setuptools import setup, find_packages

VERSION = (1, 2, "0b1")
__version__ = VERSION
__versionstr__ = ".".join(map(str, VERSION))

here = path.abspath(path.dirname(__file__))
installation_requirements = [
    "requests>=2.0.0, <3.0.0",
    "PyVCF3>=1.0.0",
    "jsonmodels>=2.2",
]
if sys.version_info < (3, 4):
    installation_requirements.extend(["asyncio", "unittest2"])
setup(
    name="varsome_api_client",
    version=__versionstr__,
    packages=find_packages(
        ".",
    ),
    scripts=["scripts/varsome_api_run.py", "scripts/varsome_api_annotate_vcf.py"],
    url="https://github.com/saphetor/varsome-api-client-python",
    license="Apache License, Version 2.0",
    test_suite="nose.collector",
    tests_require=["nose"],
    include_package_data=True,
    package_data={
        "": ["*.vcf", "*.csv"],
    },
    author="Saphetor S.A.",
    author_email="support@saphetor.com",
    description="A basic python api client implementation for https://api.varsome.com",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: Apache License",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    install_requires=installation_requirements,
    python_requires=">=3.3",
)
