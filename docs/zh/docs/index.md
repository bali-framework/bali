# 


<p align="center">
  <img src="https://raw.githubusercontent.com/bali-framework/bali/master/docs/img/bali.png" alt='bali framework' />
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

## 简介

简化基于 FastAPI 和 gRPC 的云原生微服务开发。如果你想让你的项目同时支持 HTTP 和 gRPC ,那么 Bali 可以帮助你很轻松的完成。 

Bali 的特性：

* 项目结构简单。
* 融合了 `SQLAlchemy` 并提供了 model 生成的方法。
* 提供了工具类转换 model 成为 Pydantic 模式.
* 支持 GZip 解压缩.
* 🍻 **Resource** 层处理对外服务即支持 HTTP 又支持 gRPC

## 谁在使用 Bali 框架

<a href="https://www.360shuke.com/">
    <img width="200" src="https://raw.githubusercontent.com/bali-framework/bali/master/docs/img/cases/qfin.png" />
</a>

## 依赖

1. Python 3.8+
2. FastAPI 0.63+
3. grpcio>=1.32.0,<1.42

## 安装

```shell
# Bali framework
pip install bali-core 

# Bali command line tool 
pip install bali-cli  
```
