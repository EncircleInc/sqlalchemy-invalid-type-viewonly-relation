from sqlalchemy import Column, Integer, String, ForeignKey, create_engine, inspect
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Query, aliased, sessionmaker, relationship
from sqlalchemy.sql import alias
from sqlalchemy.sql.util import ColumnAdapter
from sqlalchemy.sql.visitors import ReplacingCloningVisitor

Base = declarative_base()

class Parent(Base):
    __tablename__ = 'parents'

    id = Column(Integer, primary_key=True)
    child_type = Column(String(), nullable=False)

    __mapper_args__ = {
        'polymorphic_on': child_type,
        'with_polymorphic': '*'
    }

class Child1(Parent):
    __tablename__ = 'children_1'

    id = Column(Integer, ForeignKey(Parent.id), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'child1',
    }

class Child2(Parent):
    __tablename__ = 'children_2'

    id = Column(Integer, ForeignKey(Parent.id), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'child2',
    }

class Other(Base):
    __tablename__ = 'others'

    id = Column(Integer, primary_key=True)
    parent_id = Column(Integer, ForeignKey(Parent.id))

    parent = relationship(Parent)
    child2 = relationship(Child2, viewonly=True)

engine = create_engine('sqlite://')
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)

data_creation_session = Session()

obj = Other(parent=Child1())
data_creation_session.add(obj)
data_creation_session.commit()
obj_id = obj.id
data_creation_session.close()
del data_creation_session

# This is fine
load_child2_first_session = Session()
obj = load_child2_first_session.query(Other).get(obj_id)
assert obj.child2 is None
assert obj.parent is not None

# This is not fine
load_parent_first_session = Session()
obj = load_parent_first_session.query(Other).get(obj_id)
assert obj.parent is not None
assert obj.child2 is None, f"{obj.child2} is a {type(obj.child2)}" # Explodes
