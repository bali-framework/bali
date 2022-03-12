# ===========
# = Base Image
# ===========
#

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8-slim

# ===========
# = Author
# ===========
#

LABEL maintainer="bali-framework"

# ===========
# = Initiate Project
# ===========
#

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install tzdata locales -y \
    && sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen \
    && sed -i -e 's/# id_ID.UTF-8 UTF-8/id_ID.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen \
    && pip install pytest pytest-mock pytest-cov allure-pytest \
    && pip install bali-core

# Add Tini
ENV TINI_VERSION v0.18.0
ADD https://github.com/krallin/tini/releases/download/${TINI_VERSION}/tini /tini
RUN chmod +x /tini
