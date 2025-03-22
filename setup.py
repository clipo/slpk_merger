from setuptools import setup

setup(
    name='slpk-merger-folder',
    version='0.3',
    py_modules=['slpk_merger'],
    entry_points={
        'console_scripts': [
            'slpk-merge=slpk_merge_cli:main',
        ],
    },
    install_requires=['tqdm'],
)
