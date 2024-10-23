import pandas as pd
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base, Agency, Profession, Ethnicity, Gender, Employee
from src.load_flow import AgencyLoader, ProfessionLoader, EmployeeProcessor


@pytest.fixture(scope='module')
def setup_database():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)
    return session


@pytest.fixture
def session(setup_database):
    session = setup_database()
    yield session
    session.close()


def test_agency_loader(session):
    df = pd.DataFrame({"agency_name": ["Agency 1", "Agency 2"]})
    loader = AgencyLoader(df)
    loader.load(session)

    agencies = session.query(Agency).all()
    assert len(agencies) == 2
    assert agencies[0].name == "Agency 1"
    assert agencies[1].name == "Agency 2"


def test_profession_loader(session):
    df = pd.DataFrame({"class_title": ["Profession 1", "Profession 2"]})
    loader = ProfessionLoader(df)
    loader.load(session)

    professions = session.query(Profession).all()
    assert len(professions) == 2
    assert professions[0].name == "Profession 1"
    assert professions[1].name == "Profession 2"


def test_employee_processor(session):
    session.add(Agency(name="Agency 1"))
    session.add(Profession(name="Profession 1"))
    session.add(Ethnicity(name="Ethnicity 1"))
    session.add(Gender(name="Gender 1"))
    session.commit()

    df = pd.DataFrame({
        "first_name": ["John"],
        "last_name": ["Doe"],
        "agency_name": ["Agency 1"],
        "class_title": ["Profession 1"],
        "ethnicity": ["Ethnicity 1"],
        "gender": ["Gender 1"],
        "monthly": [5000.00]
    })

    processor = EmployeeProcessor(df, session)
    processor.process_and_save()

    employees = session.query(Employee).all()
    assert len(employees) == 1
    assert employees[0].first_name == "John"
    assert employees[0].last_name == "Doe"
