import bali
from setuptools import find_packages, setup

INSTALL_REQUIREMENTS = [
    'dateparser==1.0.0',
    'decamelize==0.1.2',
    'fastapi[all]==0.63.0',
    'fastapi-pagination==0.7.0',
    'grpcio==1.32.0',
    'grpcio-tools==1.32.0',
    'grpc-interceptor==0.13.0',
    'PyMySQL==0.10.1',
    'passlib[bcrypt]==1.7.2',
    'pillow==7.2.0',
    'protobuf==3.13.0',
    'python-jose[cryptography]==3.2.0',
    'pydantic-sqlalchemy==0.0.7',
    'redis==3.5.3',
    'SQLAlchemy==1.3.19',
    'sqla-wrapper==4.200628',
    'typer==0.3.2',
    'uvicorn==0.12.3',
]

setup(
    name='bali-core',
    version=bali.__version__,
    description='Simplify gRPC services and clients',
    url='https://github.com/JoshYuJump/bali',
    author='Josh.Yu',
    author_email='josh.yu_8@live.com',
    license='MIT',
    install_requires=INSTALL_REQUIREMENTS,
    packages=find_packages(),
    package_data={'bali': ['db/*.pyi']},
    include_package_data=True,
    zip_safe=False,
)
