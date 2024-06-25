""" A DICOM Implementation for Orthodontic Images
"""

import io
import re

# To use a consistent encoding
import codecs
from os import path

from setuptools import setup, find_packages

init_py = io.open('dicom4ortho/__init__.py').read()
metadata = dict(re.findall("__([a-z]+)__ = '([^']+)'", init_py))
metadata['doc'] = """A DICOM Implementation for Orthodontic Images"""

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with codecs.open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dicom4ortho',  # Required
    version='0.3.2',  # Required
    description=metadata['doc'],  # Required
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url=metadata['url'],
    author=metadata['author'],
    author_email=metadata['email'],
    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Healthcare Industry',
        'Topic :: Scientific/Engineering :: Medical Science Apps.',
        'Topic :: Scientific/Engineering :: Image Processing',

        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',

    ],
    keywords='DICOM VL Visible Light Photography Orthodontics',  # Optional

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required
    python_requires='>=3',
    install_requires=[
        'argparse',
        'pydicom',
        'pynetdicom',
        'pillow',
        'prettytable',
        'numpy'
    ],

    entry_points={  # Optional
        'console_scripts': [
            'dicom4ortho=dicom4ortho.__main__:main',
        ],
    },

    package_data={
        '': [
            'LICENSE',
            'resources/image_types.csv',
            'resources/codes.csv',
            'resources/views.csv',
        ]
    },
)
