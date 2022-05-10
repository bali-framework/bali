### Event

Messages rely on AMQP components, so they need to be configured accordingly, 
such as adding this configuration settings.py in your project.

```
class Settings:
    AMQP_CONFIGS = {
        'default':
            {
                'AMQP_SERVER_ADDRESS': 'amqp://user:password@localhost:5672',
                'EXCHANGE_NAME': 'exchange_name',
                'QUEUE_NAME': 'queue_name',
                'ROUTING_KEY': 'routing_key',
            }
    }

settings = Settings()
initialize(settings)
```

Define events
```
from bali.events import Event

class HelloEvent(Event):
    # The __amqp_name__ here defaults to default, 
    # which means that the AMQP configuration using default is used
    __amqp_name__ = 'default' 

    def dict(self, *args, **kwargs):
        # Rewrite dict to allow events to be transferred in the AMQP component in the way you define. 
        # If dict is not rewritten, the message will be {'type': self.type, 'payload': self.payload}
        return {'type': self.type, **self.payload}
```

Send events
```
dispatch(HelloEvent(type='hello', payload={'aaa':'bbb'}))
```

Event listening

First you need to define the processing of the event **handle_event** and the type of listening for the event **hello**

```
class EventHandler:
    @event_handler('hello')
    def handle_event(event):
        print(event)
```

AMQP configuration for event type
```
class Settings:
    AMQP_CONFIGS = {
        'default':
            {
                'AMQP_SERVER_ADDRESS': 'amqp://user:password@localhost:5672',
                'EXCHANGE_NAME': 'exchange_name',
                'QUEUE_NAME': 'queue_name',
                'ROUTING_KEY': 'routing_key',
            }
    }
    EVENT_TYPE_TO_AMQP = {
        'hello': 'default'
    }
    
settings = Settings()
initialize(settings)
```

Start listening for events
```
python main.py --event
```

