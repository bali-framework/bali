from bali.decorators import event_handler


class EventHandler:
    @event_handler('HelloSaid')
    def handle_hello_said(self, event):
        self.prepare(event)
        print('handle event: ', event)

    @event_handler('HiSaid')
    def handle_hi_said(self, event):
        self.prepare(event)
        print('handle event: ', event)

    def prepare(self, event):
        print('prepare event: ', event)
