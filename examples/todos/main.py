from bali import Bali

from resources import TodoResource

app = Bali()
app.register(TodoResource)

if __name__ == "__main__":
    app.start()
