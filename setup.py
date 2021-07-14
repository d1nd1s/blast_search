from setuptools import find_packages, setup

setup(
    name='blast_search',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Flask',
        'Flask-Bootstrap',
        'Flask-SQLAlchemy',
        'Flask-WTF',
        'WTForms',
        'dataclasses-json'
    ],
)