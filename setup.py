"xthulu installer"

from os.path import realpath, dirname, join
from setuptools import setup

if __name__ == '__main__':
    extra_packages = []
    _reqs = []
    _extras = {}
    abspath = realpath(dirname(__file__))

    with open(join(abspath, 'requirements.txt')) as reqfile:
        _reqs = reqfile.readlines()

    for extra in extra_packages:
        filename = f'requirements_{extra}.txt'

        with open(join(abspath, filename)) as reqfile:
            _extras[extra] = reqfile.readlines()

    setup(
        name='xthulu',
        version='0.0.1a1',
        description='Python 3 asyncio terminal server',
        url='https://git.oddnetwork.org/haliphax/xthulu',
        author='haliphax',
        license='MIT',
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.8',
            'Topic :: Communications :: BBS',
            'Topic :: Software Development :: User Interfaces',
            'Topic :: Terminals',
            'Topic :: Terminals :: SSH',
        ],
        keywords='terminal server asyncio bbs asyncssh ssh',
        packages=['xthulu'],
        install_requires=_reqs,
        extras_require=_extras
    )
