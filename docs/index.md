# 


<p align="center">
  <img src="https://raw.githubusercontent.com/bali-framework/bali/master/docs/img/bali.png" alt='bali framework'>
</p>
<p align="center">
    <em>🏝 Simplify Cloud Native Microservices development base on FastAPI and gRPC.</em>
</p>

<p align="center">
    <a href="https://pepy.tech/project/bali-core">
        <img src="https://pepy.tech/badge/bali-core" />
    </a>
    <a href="https://pypi.org/project/bali-core/">
        <img src="https://img.shields.io/pypi/v/bali-core" />
    </a>
</p>

---


## Introduction

Bali is a framework integrate FastAPI and gRPC. 
If you want to provide both HTTP and RPC, it can improve development efficiency.

It gives you the following features:

* A simple layout of file structure rule.
* Integrated `SQLAlchemy` ORM and provide generic model methods.
* Utilities of transform models to Pydantic schemas.
* GZipMiddleware included and GZip decompression enabled.
* 🍻 **Resource** layer to write code once support both HTTP and RPC

## Who's using bali framework

<a href="https://www.360shuke.com/">
    <img width="200" src="https://raw.githubusercontent.com/bali-framework/bali/master/docs/img/cases/qfin.png" />
</a>

## Requirements

1. Python 3.7+
2. FastAPI 0.63+
3. grpcio>=1.32.0,<1.42

## Installation

```shell
# Bali framework
pip install bali-core 

# Bali command line tool 
pip install bali-cli  
```
