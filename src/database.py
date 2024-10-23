from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, DeclarativeBase

engine = create_engine('sqlite:///load_flow.db')


class Base(DeclarativeBase):
    pass


class Agency(Base):
    __tablename__ = "agency"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class Profession(Base):
    __tablename__ = "profession"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class Ethnicity(Base):
    __tablename__ = "ethnicity"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class Gender(Base):
    __tablename__ = "gender"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)


class Employee(Base):
    __tablename__ = "employee"

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    agency_id = Column(Integer, ForeignKey('agency.id'), nullable=False)
    profession_id = Column(Integer, ForeignKey('profession.id'), nullable=False)
    gender_id = Column(Integer, ForeignKey('gender.id'), nullable=False)
    ethnicity_id = Column(Integer, ForeignKey('ethnicity.id'), nullable=False)
    monthly_salary = Column(Numeric(16, 2), nullable=False)
    md5 = Column(String(50), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.now)

    agency = relationship("Agency")
    profession = relationship("Profession")
    gender = relationship("Gender")
    ethnicity = relationship("Ethnicity")


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
