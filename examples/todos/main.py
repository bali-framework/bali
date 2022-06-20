from bali import Bali
from resources import TodoResource

app = Bali(title='todos')
app.register(TodoResource)

if __name__ == "__main__":
    app.start()
