from setuptools import setup, find_packages

setup(
    name='flexible-skiplist',
    version='0.1.0',
    packages=find_packages(exclude=['test*']),
    license='MIT',
    description='A flexible skiplist data structure that also supports O(logn) cumulative sums',
    long_description='''
A flexible implementation of the skiplist data structure

This implementation of skiplist unlocks the full potential of the data structure by also allowing for both sorted and non-sorted skiplists and also enabling O(logn) search by cumulative sums.

In short, it can serve as the standard sorted key-value store (as do other implementations), 
but it can also allow you to keep a non-sorted list which gives you O(logn) calculation of sums from beginning to k-th element.

Or, as was the use case the author needed but did not find, both at the same time - a sorted list with search into it also by cumulative sums.

The code is written in pure Python 3 without external dependencies and is moderately optimized.
    ''',
    install_requires=[],
    url='https://github.com/velochy/flexible_skiplist',
    author='Margus Niitsoo',
    author_email='velochy@gmail.com'
)