<p align="center">
  <img src="https://raw.githubusercontent.com/bali-framework/bali/master/docs/img/bali.png" alt='bali framework' />
</p>
<p align="center">
    <em>🏝 Simplify Cloud Native Microservices development base on FastAPI and gRPC.</em>
</p>

<p align="center">
    <a href="https://pepy.tech/project/bali-core">
        <img src="https://pepy.tech/badge/bali-core" />
    </a>
    <a href="https://pypi.org/project/bali-core/">
        <img src="https://img.shields.io/pypi/v/bali-core" />
    </a>
</p>

---

# Bali

简化基于 FastAPI 和 gRPC 的云原生微服务开发。如果你想让你的项目同时支持 HTTP 和 gRPC ,那么 Bali 可以帮助你很轻松的完成。 

Bali 的特性：

* 项目结构简单。
* 融合了 `SQLAlchemy` 并提供了 model 生成的方法。
* 提供了工具类转换 model 成为 Pydantic 模式.
* 支持 GZip 解压缩.
* 🍻 **Resource** 层处理对外服务即支持 HTTP 又支持 gRPC
* 支持 Event 发送及监听

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
```
配置好后还需要对配置初始化：
```
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

