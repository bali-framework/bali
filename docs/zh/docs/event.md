### Event

消息依赖 AMQP 组件，所以需要进行相应配置，例如在你的项目中 settings.py 里面加入这段配置

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

定义 Event 
```
from bali.events import Event

class HelloEvent(Event):
    __amqp_name__ = 'default' # 这里的 __amqp_name__ 默认就是 default ，代表使用的是 default 的 AMQP 配置

    def dict(self, *args, **kwargs):
        # 重写 dict ，可以让 event 按照你定义的方式在 AMQP 组件中传输， 如果不重写 dict，那么消息将是 {'type': self.type, 'payload': self.payload}
        return {'type': self.type, **self.payload}
```

发送事件：
```
dispatch(HelloEvent(type='hello', payload={'aaa':'bbb'}))
```

事件监听：

首先需要定义事件的处理 **handle_event** 及监听事件的类型 **hello**

```
class EventHandler:
    @event_handler('hello')
    def handle_event(event):
        print(event)
```

事件类型对应的 AMQP 配置：
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

开始监听事件：
```
python main.py --event
```

