from kombu import Connection

from bali.events import Event


def dispatch(event: Event, server_address: str):
    with Connection(server_address) as conn:
        # produce
        producer = conn.Producer(serializer='json')
        producer.publish(
            event.payload,
            exchange=event.exchange,
            routing_key=event.routing_key,
            declare=[event.queue],
            retry=True
        )
