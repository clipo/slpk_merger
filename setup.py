from setuptools import setup

setup(
    name='slpk-merger',
    version='0.2',
    py_modules=['slpk_merger'],
    entry_points={
        'console_scripts': [
            'slpk-merge=slpk_merge_cli:main',
        ],
    },
    install_requires=['tqdm'],
)
