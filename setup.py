from setuptools import find_packages
from setuptools import setup

MAJOR_VERSION = '0'
MINOR_VERSION = '0'
MICRO_VERSION = '0'
VERSION = "{}.{}.{}".format(MAJOR_VERSION, MINOR_VERSION, MICRO_VERSION)

setup(name='spacy_api',
      version=VERSION,
      description="Server/Client around Spacy to load only once",
      author='Pascal van Kooten',
      url='https://github.com/kootenpv/spacy_api',
      author_email='kootenpv@gmail.com',
      install_requires=[
          'requests', 'flask', 'spacy'
      ],
      entry_points={
          'console_scripts': ['spacy = spacy_api.__main__:main']
      },
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Operating System :: POSIX :: Linux',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: Cython',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Scientific/Engineering'
      ],
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      platforms='any')
