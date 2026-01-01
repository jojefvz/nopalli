from sqlalchemy import Table, Column, Integer, String, create_engine, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import composite, registry

from src.domain.aggregates.broker.aggregate import Broker 
from src.domain.aggregates.broker.value_objects import BrokerStatus 
from src.domain.aggregates.driver.aggregate import Driver 
from src.domain.aggregates.driver.value_objects import DriverStatus 
from src.domain.aggregates.location.aggregate import Location 
from src.domain.aggregates.location.value_objects import Address, LocationStatus 


def set_orm_mapping(engine):
    mapper_registry = registry()

    location_table = Table(
        'locations',
        mapper_registry.metadata,
        Column('id', UUID(as_uuid=True), primary_key=True),
        Column('status', Enum(LocationStatus), nullable=False),
        Column('name', String, nullable=False),
        Column('street_address', String, nullable=False),
        Column('city', String, nullable=False),
        Column('state', String, nullable=False),
        Column('zipcode', Integer, nullable=False)
    )

    broker_table = Table(
        'brokers',
        mapper_registry.metadata,
        Column('id', UUID(as_uuid=True), primary_key=True),
        Column('status', Enum(BrokerStatus), nullable=False),
        Column('name', String, nullable=False),
        Column('street_address', String, nullable=False),
        Column('city', String, nullable=False),
        Column('state', String, nullable=False),
        Column('zipcode', Integer, nullable=False)
    )

    driver_table = Table(
        'drivers',
        mapper_registry.metadata,
        Column('id', UUID(as_uuid=True), primary_key=True),
        Column('status', Enum(DriverStatus), nullable=False),
        Column('name', String, nullable=False)
    )

    # dispatch_table = Table(
    #     'dispatches',
    #     mapper_registry.metadata,
    #     Column('id', Integer, primary_key=True),
    #     Column('reference', String, unique=True),
    #     Column('status', Enum(DispatchStatus), nullable=False),
    #     Column('containers', PickleType),
    # )

    

    

    # brokers_view = Table(
    #     'brokers_view',
    #     mapper_registry.metadata,
    #     Column('id', Integer, primary_key=True),
    #     Column('name', String),
    #     Column('street_address', String),
    #     Column('city', String),
    #     Column('state', String),
    #     Column('zipcode', Integer)
    # )


    def start_mappers():
        mapper_registry.map_imperatively(
            Location, 
            location_table,
            properties={
                'address': composite(
                    Address, 
                    location_table.c.street_address, 
                    location_table.c.city, 
                    location_table.c.state, 
                    location_table.c.zipcode)
                    }
            )
        
        mapper_registry.map_imperatively(
            Broker, 
            broker_table,
            properties={
                'address': composite(
                    Address, 
                    broker_table.c.street_address, 
                    broker_table.c.city, 
                    broker_table.c.state, 
                    broker_table.c.zipcode)
                    }
            )
        
        mapper_registry.map_imperatively(Driver, driver_table)
        
        # mapper_registry.map_imperatively(
        #     Dispatch,
        #     dispatch_table,
        #     properties={'stops': relationship(Stop, backref="stops", order_by=stop_table.c.priority)}
        #     )
        # mapper_registry.map_imperatively(Stop, stop_table)

        
    
    start_mappers()
    mapper_registry.metadata.create_all(engine)