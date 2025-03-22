from setuptools import setup

setup(
    name='slpk-merger',
    version='0.1',
    py_modules=['slpk_merger'],
    entry_points={
        'console_scripts': [
            'slpk-merge=slpk_merge_cli:main',
        ],
    },
    install_requires=[],
    author='Your Name',
    description='CLI tool to merge two Esri SLPK files',
)
