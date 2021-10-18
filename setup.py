import bali
from setuptools import find_packages, setup


def read(f):
    return open(f, 'r', encoding='utf-8').read()


# https://pip.pypa.io/en/latest/user_guide/#fixing-conflicting-dependencies
INSTALL_REQUIREMENTS = read('requirements.txt').splitlines()

setup(
    name='bali-core',
    version=bali.__version__,
    description='Simplify FastAPI integrate gRPC services development',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/JoshYuJump/bali',
    author='Josh.Yu',
    author_email='josh.yu_8@live.com',
    license='MIT',
    install_requires=INSTALL_REQUIREMENTS,
    packages=find_packages(exclude=['examples', 'examples.*', 'tests']),
    package_data={'bali': ['db/*.pyi']},
    include_package_data=True,
    zip_safe=False,
)
