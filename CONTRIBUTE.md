# CONTRIBUTE

## Developer Environment


1. Python requirements
```bash
# Install python requirement in your environment.
pip install -r requirements_dev.txt
``` 


2. Redis 

The test Redis host is 127.0.0.1, or setting by environment variable `CACHE_HOST`.   

Its password is setting by environment variable `CACHE_PASSWORD`.


3. RabbitMQ

RabbitMQ for test is settings by environment variable `AMQP_SERVER_ADDRESS`.


## Tag a new release

tag a version:

```bash
git tag -a v0.1.0
```

push tags to remote:

```bash
git push --tags
```


## Maintenance documents

```bash
# English version (default)
mkdocs serve
# Chinese version
cd docs/zh && mkdocs serve
```

