from bali import Bali
from bali.declarative import *

API("Greeter").get({"Hello": "Bali Declarative"})

app = Bali()

if __name__ == "__main__":
    app.start()
