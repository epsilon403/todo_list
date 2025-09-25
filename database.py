from sqlalchemy import (
    Table,
    MetaData,
    Column,
    Integer,
    String,
    Numeric,
    DateTime,
    Text,
    ForeignKey,
    CheckConstraint,
    text,
    create_engine,
    Select,
    or_,
    desc,
    Enum ,
    Boolean
)
meta = MetaData()



user_table = Table(
    "user",
    meta ,
    Column('id' ,Integer, primary_key=True),
    Column("name" , String(30)),
    Column("last name" , String(30))
)
tasks_table = Table(
    "tasks",
    meta,
    Column('id' , Integer , primary_key=True),
    Column('title' , String(50) , unique=True),
    Column('description' , Text , nullable=True),
    Column('priority' , Enum('red' , 'green' , 'yellow' ,name = 'priority_enum_type')),
    Column('completed', Enum('undone' , 'done' ,name = 'completed_status' ) ,  server_default='undone') 
)

engine = create_engine('postgresql://postgres:epsilon2001@localhost:5432/to_do_list')

meta.create_all(engine)