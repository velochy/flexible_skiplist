from setuptools import setup, find_packages

setup(
    name='flexible-skiplist',
    version='0.0.1',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='A flexible skiplist data structure that also supports O(logn) cumulative sums',
    long_description=open('README.md').read(),
    install_requires=[],
    url='https://github.com/velochy/flexible_skiplist',
    author='Margus Niitsoo',
    author_email='velochy@gmail.com'
)