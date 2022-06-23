import os
import sys


class TestEnvironments:
    def test_default_environment(self):
        from bali.environments import ENV, STAGE
        assert ENV == STAGE.DEV

    def test_set_environment(self):
        os.environ['ENV'] = 'TEST'

        try:
            del sys.modules["bali.environments"]
        except KeyError:
            pass

        from bali.environments import ENV, STAGE
        assert ENV == STAGE.TEST
