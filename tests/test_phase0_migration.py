
import pytest
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.domain.models import Base, ProductModel, ProductAliasModel, CollectionItemModel, UserModel
from scripts.phase0_migration import migrate_excel_to_db

@pytest.fixture
def db_session():
    """In-memory SQLite for testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Create default user
    admin = UserModel(username="admin", email="admin@eternia.com", hashed_password="hashed", role="admin")
    session.add(admin)
    session.commit()
    
    yield session
    session.close()

def test_migration_logic(db_session, tmp_path):
    """
    Simulates Excel data and tests the migration function.
    """
    # 1. Create Mock Excel
    excel_data = {
        'Adquirido': ['S', 'No'],
        'Name': ['He-Man', 'Skeletor'],
        'Wave': ['1', '1'],
        'Year': ['2020', '2020'],
        'Retail': ['$14.99', '$14.99'],
        'Imagen': ['Ver Imagen', 'Ver Imagen'],
        'Image Path': ['path/to/img1.jpg', 'path/to/img2.jpg'],
        'Image URL': ['http://411.com/img1.jpg', 'http://411.com/img2.jpg'],
        'Detail Link': ['http://411.com/heman', 'http://411.com/skeletor'],
        'Figure ID': ['2393', '2394']
    }
    df = pd.DataFrame(excel_data)
    excel_file = tmp_path / "mock_motu.xlsx"
    
    # We need multiple sheets as in the real file
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=1)
        # Add the title row that the real Excel has at row 0
        worksheet = writer.sheets['Sheet1']
        worksheet.write(0, 0, "Mock Checklist")
        # Add headers manually because to_excel writes them at startrow
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(1, col_num, value)

    # 2. Run Migration
    migrate_excel_to_db(str(excel_file), db_session)
    
    # 3. Assertions
    products = db_session.query(ProductModel).all()
    assert len(products) == 2
    
    heman = db_session.query(ProductModel).filter_by(figure_id="2393").first()
    assert heman.name == "He-Man"
    
    # Check Alias
    alias = db_session.query(ProductAliasModel).filter_by(source_url="http://411.com/heman").first()
    assert alias.product_id == heman.id
    
    # Check Collection
    collected = db_session.query(CollectionItemModel).filter_by(product_id=heman.id).first()
    assert collected is not None
    assert collected.acquired == True
    
    skeletor = db_session.query(ProductModel).filter_by(figure_id="2394").first()
    collected_sk = db_session.query(CollectionItemModel).filter_by(product_id=skeletor.id).first()
    assert collected_sk.acquired == False

def test_deduplication(db_session, tmp_path):
    """Verifies that running twice doesn't create dupes."""
    excel_data = {
        'Adquirido': ['S'],
        'Name': ['He-Man'],
        'Wave': ['1'],
        'Year': ['2020'],
        'Retail': ['$14.99'],
        'Imagen': ['Ver Imagen'],
        'Image Path': ['path/to/img1.jpg'],
        'Image URL': ['http://411.com/img1.jpg'],
        'Detail Link': ['http://411.com/heman'],
        'Figure ID': ['2393']
    }
    df = pd.DataFrame(excel_data)
    excel_file = tmp_path / "mock_motu.xlsx"
    
    with pd.ExcelWriter(excel_file, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=1)
        worksheet = writer.sheets['Sheet1']
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(1, col_num, value)

    # Run twice
    migrate_excel_to_db(str(excel_file), db_session)
    migrate_excel_to_db(str(excel_file), db_session)
    
    products = db_session.query(ProductModel).all()
    assert len(products) == 1
    
    aliases = db_session.query(ProductAliasModel).all()
    assert len(aliases) == 1
