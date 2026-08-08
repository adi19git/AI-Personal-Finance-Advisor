from sqlalchemy import create_engine, select, func, extract, Column, Integer, Date
from sqlalchemy.orm import declarative_base, Session
import datetime

Base = declarative_base()

class Dummy(Base):
    __tablename__ = 'dummy'
    id = Column(Integer, primary_key=True)
    date = Column(Date)
    val = Column(Integer)

engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)

with Session(engine) as session:
    session.add(Dummy(date=datetime.date(2026, 8, 1), val=50))
    session.add(Dummy(date=datetime.date(2026, 8, 2), val=20))
    session.commit()
    
    # test extract
    y = 2026
    m = 8
    res = session.scalar(select(func.sum(Dummy.val)).filter(
        extract('year', Dummy.date) == y,
        extract('month', Dummy.date) == m
    ))
    print("Extract result:", res)
