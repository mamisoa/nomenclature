import ast
import datetime
import json
import xml.etree.ElementTree as ET

from dotenv import dotenv_values
from sqlalchemy import MetaData, create_engine, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func

config = dotenv_values(".env")

# Database connection details
DATABASE_URL = f'mysql+pymysql://{config["DATABASE_USER"]}:{config["DATABASE_PASSWORD"]}@{config["DATABASE_URL"]}/{config['DATABASE']}'

# Establishing connection to the database
engine = create_engine(DATABASE_URL)
metadata = MetaData()

# Reflect existing database tables into the new MetaData object
metadata.reflect(bind=engine)
Session = sessionmaker(bind=engine)


def process_xml_and_update_db(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    nomenclature = metadata.tables['nomenclature']

    session = Session()

    try:
        for entry in root.findall('.//nomen_code_entry'):
            code = entry.get('code')
            desc_fr = entry.find('desc_fr').text if entry.find('desc_fr') is not None else ''
            desc_nl = entry.find('desc_nl').text if entry.find('desc_nl') is not None else ''
            code_desc = f"{desc_fr} / {desc_nl}"
            cout = entry.find('cout').text if entry.find('cout') is not None else '[0,0,0,0]'
            # Prepare data dictionary here
            data = {
                "date": datetime.datetime.now(),
                "code": code,
                "code_desc": code_desc,
                "price_list": cout,
                "supplement_ratio": 1.54
            }
            # print("data:", data, "cout:", ast.literal_eval(cout))

            # Check if the code already exists
            result = session.execute(select(func.count()).select_from(nomenclature).where(nomenclature.c.code == code)).scalar()

            if result > 0:
                # Update existing record
                update_stmt = nomenclature.update().where(nomenclature.c.code == code).values(**data)
                session.execute(update_stmt)
            else:
                # Insert new record
                insert_stmt = nomenclature.insert().values(**data)
                session.execute(insert_stmt)

        session.commit()  # Commit all changes
    except Exception as e:
        session.rollback()  # Rollback changes on error
        print(f"Error: {e}")
    finally:
        session.close()  # Close the session

xml_file_path = './transformed.xml'
process_xml_and_update_db(xml_file_path)
