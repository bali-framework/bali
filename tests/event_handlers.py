from bali import event_handler


class EventHandler:
    @event_handler("event_type")
    def handle_event(self, event):
        print("Event handler received: ", event)
