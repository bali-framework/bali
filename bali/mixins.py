from .core import db


# noinspection PyMethodMayBeStatic
class ServiceMixin:
    def setup(self):
        pass

    def teardown(self):
        # noinspection PyBroadException
        try:
            db.remove()
        except Exception:
            pass

    def __getattribute__(self, attr, *args, **kwargs):
        if attr in ['setup', 'teardown']:
            return super().__getattribute__(attr)

        self.setup()
        result = super().__getattribute__(attr)
        self.teardown()
        return result
