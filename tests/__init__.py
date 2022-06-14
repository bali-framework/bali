import os
import sys

# Added `tests/test_services` to python path
services_path = os.path.join(sys.path[0], 'tests', 'test_services')

if services_path not in sys.path:
    sys.path.append(services_path)
