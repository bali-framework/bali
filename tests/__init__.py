import os
import sys

# Added `tests/test_services` to python path
services_path = os.path.join(sys.path[0], 'tests', 'test_services')
services_protos_path = os.path.join(services_path, 'protos')

for path in [services_path, services_protos_path]:
    if path not in sys.path:
        sys.path.append(path)
