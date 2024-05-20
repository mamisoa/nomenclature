import datetime
import xml.etree.ElementTree as ET

from dotenv import load_dotenv
from sqlalchemy import MetaData, Table, and_, create_engine, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import func

load_dotenv()


# Database connection details
DATABASE_URL = "mysql+pymysql://username:password@localhost/py4web"

# Establishing connection to the database
engine = create_engine(DATABASE_URL)
metadata = MetaData(bind=engine)
nomenclature = Table("nomenclature", metadata, autoload_with=engine)


def process_xml_and_update_db(xml_path):
    # Parse the XML file
    tree = ET.parse(xml_path)
    root = tree.getroot()

    with engine.connect() as connection:
        for entry in root.findall(".//nomen_code_entry"):
            code = entry.get("code")
            desc_fr = (
                entry.find("desc_fr").text if entry.find("desc_fr") is not None else ""
            )
            desc_nl = (
                entry.find("desc_nl").text if entry.find("desc_nl") is not None else ""
            )
            code_desc = f"{desc_fr} {desc_nl}"
            cout = (
                entry.find("cout").text
                if entry.find("cout") is not None
                else "[0,0,0,0]"
            )

            # Prepare data
            data = {
                "date": datetime.datetime.now(),
                "code": code,
                "code_desc": code_desc,
                "price_list": cout,
            }

            # Check if the code already exists
            stmt = (
                select([func.count()])
                .select_from(nomenclature)
                .where(nomenclature.c.code == code)
            )
            result = connection.execute(stmt)

            if result.scalar() > 0:
                # Update existing record
                update_stmt = (
                    nomenclature.update()
                    .where(nomenclature.c.code == code)
                    .values(**data)
                )
                connection.execute(update_stmt)
            else:
                # Insert new record
                insert_stmt = nomenclature.insert().values(**data)
                try:
                    connection.execute(insert_stmt)
                except IntegrityError:
                    print(
                        f"Failed to insert record with code {code} due to integrity error."
                    )


xml_file_path = "./transformed.xml"
process_xml_and_update_db(xml_file_path)
