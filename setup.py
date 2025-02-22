"""
@author linnan
@time 2024/06/07
"""

from setuptools import setup, find_packages

setup(
    name='lntools',
    version='0.1.0',
    description="ln gentools",
    author='linnan',
    author_email='lnonly@163.com',
    python_requires='>=3.11',
    packages=find_packages(where="."),
    package_data={
        'lntools': [
            'config/*.yaml',
            'config/*.ini'
        ]
    },
    include_package_data=True,
    install_requires=[      
        'numpy',
        'pandas',
        'polars',
        'rich',
        'pyyaml',
        'pyarrow',
    ],
    zip_safe=False,
)