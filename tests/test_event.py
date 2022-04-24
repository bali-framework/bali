def test_event_dispatch():
    from bali.events import Event, dispatch
    from bali.core import _settings
    _settings.AMQP_CONFIGS = {
        'default':
            {
                'AMQP_SERVER_ADDRESS': 'amqp://192.168.99.100:5672',
                'EXCHANGE_NAME': 'test_exchange',
                'QUEUE_NAME': 'test_queue',
                'ROUTING_KEY': 'test_routing_key'
            }
    }
    event = Event(type='test', payload={'hello': 'world'})
    assert dispatch(event)
