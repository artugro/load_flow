from abc import ABC, abstractmethod
from hashlib import md5

import pandas as pd
from sqlalchemy.exc import IntegrityError

from database import Agency, Profession, Ethnicity, Gender, Employee, session


class CatalogLoader(ABC):
    @abstractmethod
    def load(self, db_session):
        pass


class AgencyLoader(CatalogLoader):
    def __init__(self, df):
        self.df = df

    def load(self, db_session):
        for row in self.df["agency_name"].dropna():
            if row:
                if not db_session.query(Agency).filter_by(name=row).first():
                    db_session.add(Agency(name=row))
        db_session.commit()


class ProfessionLoader(CatalogLoader):
    def __init__(self, df):
        self.df = df

    def load(self, db_session):
        for row in self.df["class_title"].dropna():
            if row:
                if not db_session.query(Profession).filter_by(name=row).first():
                    db_session.add(Profession(name=row))
        db_session.commit()


class EthnicityLoader(CatalogLoader):
    def __init__(self, df):
        self.df = df

    def load(self, db_session):
        for row in self.df["ethnicity"].dropna():
            if row:
                if not db_session.query(Ethnicity).filter_by(name=row).first():
                    db_session.add(Ethnicity(name=row))
        db_session.commit()


class GenderLoader(CatalogLoader):
    def __init__(self, df):
        self.df = df

    def load(self, db_session):
        for row in self.df["gender"].dropna():
            if row:
                if not db_session.query(Gender).filter_by(name=row).first():
                    db_session.add(Gender(name=row))
        db_session.commit()


class EmployeeProcessor:
    def __init__(self, df, db_session):
        self.df = df
        self.db_session = db_session

    def get_catalog_id(self, model_class, name):
        instance = self.db_session.query(model_class).filter_by(name=name).first()
        return instance.id if instance else None

    @staticmethod
    def generate_md5(employee_data):
        string_to_hash = (f"{employee_data['first_name']}{employee_data['last_name']}{employee_data['profession_id']}"
                          f"{employee_data['ethnicity_id']}{employee_data['gender_id']}")
        return md5(string_to_hash.encode()).hexdigest()

    def process_and_save(self):
        employees_data = []
        for _, row in self.df.iterrows():
            agency_id = self.get_catalog_id(Agency, row['agency_name'])
            profession_id = self.get_catalog_id(Profession, row['class_title'])
            ethnicity_id = self.get_catalog_id(Ethnicity, row['ethnicity'])
            gender_id = self.get_catalog_id(Gender, row['gender'])

            if agency_id and profession_id and ethnicity_id and gender_id:
                employee_data = {
                    "first_name": row["first_name"],
                    "last_name": row["last_name"],
                    "agency_id": agency_id,
                    "profession_id": profession_id,
                    "ethnicity_id": ethnicity_id,
                    "gender_id": gender_id,
                    "monthly_salary": row["monthly"]
                }
                employee_data['md5'] = self.generate_md5(employee_data)

                existing_employee = self.db_session.query(Employee).filter_by(md5=employee_data['md5']).first()

                if not existing_employee:
                    employees_data.append(Employee(**employee_data))

            if len(employees_data) >= 10000:
                try:
                    self.db_session.add_all(employees_data)
                    self.db_session.commit()
                except IntegrityError:
                    self.db_session.rollback()
                employees_data = []

        if employees_data:
            try:
                self.db_session.add_all(employees_data)
                self.db_session.commit()
            except IntegrityError:
                self.db_session.rollback()
            employees_data = []


class ETLProcess:
    def __init__(self, db_session, catalog_loaders, employee_processor):
        self.session = db_session
        self.catalog_loaders = catalog_loaders
        self.employee_processor = employee_processor

    def run(self):
        db_session = self.session
        try:
            for loader in self.catalog_loaders:
                loader.load(db_session)
            self.employee_processor.process_and_save()
        finally:
            session.close()


def run_etl_process(db_session):
    catalog_df = pd.read_csv("./catalogos.csv", sep=";")

    agency_loader = AgencyLoader(catalog_df)
    profession_loader = ProfessionLoader(catalog_df)
    ethnicity_loader = EthnicityLoader(catalog_df)
    gender_loader = GenderLoader(catalog_df)

    employees_df = pd.read_csv("./employees.csv")

    employee_processor = EmployeeProcessor(employees_df, db_session)

    etl = ETLProcess(
        db_session=db_session,
        catalog_loaders=[agency_loader, profession_loader, ethnicity_loader, gender_loader],
        employee_processor=employee_processor
    )

    etl.run()
    print("ETL Process completed successfully.")


if __name__ == "__main__":
    run_etl_process(session)
