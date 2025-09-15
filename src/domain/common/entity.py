from uuid import uuid4


class Entity:
    def __init__(self):
        self.id = uuid4()

class AggregateRoot(Entity):
    pass