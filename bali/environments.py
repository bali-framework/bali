"""
Environments

There a two style:
1. `default` style
    development, testing, staging, production
    ref: https://en.wikipedia.org/wiki/Deployment_environment#Environments
2. `abbreviation` style
    DEV, TEST, STAGING, PROD
    ref: https://medium.com/@buttertechn/qa-testing-what-is-dev-sit-uat-prod-ac97965ce4f

For historical reasons, `abbreviation` style is chosen.
You are welcome to submit a PR compatible `default` style.
"""

import logging
import os
from enum import Enum

logger = logging.getLogger('bali')


# noinspection PyArgumentList
STAGE = Enum('Stage', [
    'DEV',
    'TEST',
    'STAGING',
    'PROD',
])
env = os.environ.get('ENV', STAGE.DEV.name)

if env not in STAGE.__members__:
    logger.error('Provided ENV error: %s', env)
    env = 'DEV'

ENV = STAGE[env]
