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
    url='https://github.com/bali-framework/bali',
    author='Josh.Yu',
    author_email='josh.yu_8@live.com',
    license='MIT',
    install_requires=INSTALL_REQUIREMENTS,
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 5 - Production/Stable',
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Internet :: WWW/HTTP",
        "Environment :: Web Environment",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(
        exclude=[
            'examples',
            'examples.*',
            'tests',
            'tests.*',
            'docker',
            'docs',
        ]
    ),
    package_data={'bali': ['db/*.pyi']},
    include_package_data=True,
    zip_safe=False,
)
