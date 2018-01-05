from setuptools import setup
from os import path

VERSION = (2, 0, '0b1')
__version__ = VERSION
__versionstr__ = '.'.join(map(str, VERSION))

here = path.abspath(path.dirname(__file__))

setup(
    name='variant_api',
    version=__versionstr__,
    packages=['variantapi'],
    url='https://github.com/saphetor/variant-api-client-python',
    license='Apache License, Version 2.0',
    package_data={'': ['annotate_vcf.py', 'run.py']},
    author='Saphetor',
    author_email='support@saphetor.com',
    description='A basic python api client implementation for https://api.varsome.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: Apache License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=[
        'requests>=2.0.0, <3.0.0',
        'PyVCF>=0.6.8',
        'jsonmodels>=2.2'
    ],
)
