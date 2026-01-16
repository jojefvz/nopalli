from sqlalchemy import Date, DateTime, ForeignKey, Sequence, Table, Column, Integer, String, Enum, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import composite, registry, relationship

from src.domain.aggregates.broker.aggregate import Broker 
from src.domain.aggregates.broker.value_objects import BrokerStatus 
from src.domain.aggregates.dispatch.aggregate import Dispatch
from src.domain.aggregates.dispatch.entities import Task
from src.domain.aggregates.driver.aggregate import Driver 
from src.domain.aggregates.driver.value_objects import DriverStatus
from src.domain.aggregates.dispatch.value_objects import Appointment, AppointmentType, Container, DispatchStatus, Instruction, TaskStatus
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

    task_table = Table(
        'tasks',
        mapper_registry.metadata,
        Column('id', UUID(as_uuid=True), primary_key=True),
        Column('dispatch_id', UUID(as_uuid=True), ForeignKey('dispatches.id'), nullable=False),
        Column('status', Enum(TaskStatus), nullable=False),
        Column('priority', Integer, nullable=False),
        Column('instruction', Enum(Instruction), nullable=False),
        Column('date', Date, nullable=False),
        Column('location_id', UUID(as_uuid=True), ForeignKey('locations.id'), nullable=True),
        Column('container_number', String, nullable=True),
        Column('appointment_type', Enum(AppointmentType), nullable=True),
        Column('appointment_start_time', Time, nullable=True),
        Column('appointment_end_time', Time, nullable=True),
        Column('driver_id', UUID(as_uuid=True), ForeignKey('drivers.id'), nullable=True),
        Column('check_in', DateTime, nullable=True),
        Column('check_out', DateTime, nullable=True)
    )

    dispatch_table = Table(
        'dispatches',
        mapper_registry.metadata,
        Column('id', UUID(as_uuid=True), primary_key=True),
        Column(
            'reference', 
            Integer, 
            Sequence('dispatch_reference_seq', start=10000, increment=1),
            nullable=False, 
            unique=True
        ),
        Column('status', Enum(DispatchStatus), nullable=False),
        Column('broker_id', UUID(as_uuid=True), ForeignKey('brokers.id'), nullable=False),
        Column('driver_id', UUID(as_uuid=True), ForeignKey('drivers.id'), nullable=True)
    )



    def start_mappers():
        mapper_registry.map_imperatively(
            Location, 
            location_table,
            properties={
                '_status': location_table.c.status,
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
                '_status': broker_table.c.status,
                'address': composite(
                    Address, 
                    broker_table.c.street_address, 
                    broker_table.c.city, 
                    broker_table.c.state, 
                    broker_table.c.zipcode)
                }
            )
        
        mapper_registry.map_imperatively(
            Driver,
            driver_table,
            properties={
               '_status': driver_table.c.status, 
            })
        
        mapper_registry.map_imperatively(
            Task,
            task_table,
            properties={
                '_status': task_table.c.status,
                'location': relationship(
                   Location,
                   lazy='joined',
                   foreign_keys=[task_table.c.location_id],
                   ),
                'container': composite(Container, task_table.c.container_number),
                'appointment': composite(
                    Appointment,
                    task_table.c.appointment_type,
                    task_table.c.appointment_start_time,
                    task_table.c.appointment_end_time,
                    ),
                'completed_by': relationship(
                    Driver,
                    lazy='joined',
                    foreign_keys=[task_table.c.driver_id]
                    )
            })
        
        mapper_registry.map_imperatively(
            Dispatch,
            dispatch_table,
            properties={
                'reference': dispatch_table.c.reference,
                '_status': dispatch_table.c.status,
                'broker': relationship(
                   Broker,
                   lazy='joined',
                   foreign_keys=[dispatch_table.c.broker_id],
                   backref=None
                   ),
                'driver': relationship(
                   Driver,
                   lazy='joined',
                   foreign_keys=[dispatch_table.c.driver_id],
                   backref=None
                   ),
                'plan': relationship(
                    Task, 
                    lazy="selectin", 
                    foreign_keys=[task_table.c.dispatch_id],
                    cascade='all, delete-orphan',
                    order_by=task_table.c.priority,
                    backref=None
                    ),
                }
            )
    
    start_mappers()
    mapper_registry.metadata.create_all(engine)