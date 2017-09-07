try:
    import setuptools
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def discover_and_run_tests():
    import os
    import sys
    import unittest

    # get setup.py directory
    setup_file = sys.modules['__main__'].__file__
    setup_dir = os.path.abspath(os.path.dirname(setup_file))

    # use the default shared TestLoader instance
    test_loader = unittest.defaultTestLoader

    # use the basic test runner that outputs to sys.stderr
    test_runner = unittest.TextTestRunner()

    # automatically discover all tests
    # NOTE: only works for python 2.7 and later
    test_suite = test_loader.discover(setup_dir+'/tests')

    # run the test suite
    test_runner.run(test_suite)

try:
    from setuptools.command.test import test

    class DiscoverTest(test):

        def finalize_options(self):
            test.finalize_options(self)
            self.test_args = []
            self.test_suite = True

        def run_tests(self):
            discover_and_run_tests()

except ImportError:
    from distutils.core import Command

    class DiscoverTest(Command):
        user_options = []

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            discover_and_run_tests()

VERSION = '0.1.0'
setup(
    name='pyrpmspec',
    packages=setuptools.find_packages(),
    version=VERSION,
    description='generate spec file to build rpm',
    author='Allan',
    author_email='hung.allan@gmail.com',
    url='https://github.com/hungallan/pyrpmspec',
    download_url='https://github.com/hungallan/pyrpmspec/tarball/' + VERSION,
    keywords=['utility', 'miscellaneous', 'library'],
    classifiers=[],
    entry_points={                                                                                                                                                                                                                                                             
        'console_scripts': [                                                                                                                                                                                                                                                   
            'pyrpmspec = pyrpmspec.pyrpmspec:main',                                                                                                                                                                                                                          
        ]
    },
    cmdclass={'test': DiscoverTest}
)
