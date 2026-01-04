
import unittest
import os
import sys
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

# Add src to path
root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from src.domain.models import Base, ProductModel, ProductAliasModel, CollectionItemModel, UserModel
from scripts.phase0_migration import migrate_excel_to_db

class TestPhase0Migration(unittest.TestCase):
    def setUp(self):
        """In-memory SQLite for testing."""
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()
        
        # Create default user
        admin = UserModel(username="admin", email="admin@eternia.com", hashed_password="hashed", role="admin")
        self.session.add(admin)
        self.session.commit()
        
        self.tmp_excel = "mock_motu_test.xlsx"

    def tearDown(self):
        self.session.close()
        if os.path.exists(self.tmp_excel):
            os.remove(self.tmp_excel)

    def test_migration_logic(self):
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
        
        with pd.ExcelWriter(self.tmp_excel, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=1)
            worksheet = writer.sheets['Sheet1']
            worksheet.write(0, 0, "Mock Checklist")
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(1, col_num, value)

        # 2. Run Migration
        migrate_excel_to_db(self.tmp_excel, self.session)
        
        # 3. Assertions
        products = self.session.query(ProductModel).all()
        self.assertEqual(len(products), 2)
        
        heman = self.session.query(ProductModel).filter_by(figure_id="2393").first()
        self.assertEqual(heman.name, "He-Man")
        
        # Check Alias
        alias = self.session.query(ProductAliasModel).filter_by(source_url="http://411.com/heman").first()
        self.assertEqual(alias.product_id, heman.id)
        
        # Check Collection
        collected = self.session.query(CollectionItemModel).filter_by(product_id=heman.id).first()
        self.assertIsNotNone(collected)
        self.assertTrue(collected.acquired)

    def test_deduplication(self):
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
        
        with pd.ExcelWriter(self.tmp_excel, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False, startrow=1)
            worksheet = writer.sheets['Sheet1']
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(1, col_num, value)

        # Run twice
        migrate_excel_to_db(self.tmp_excel, self.session)
        migrate_excel_to_db(self.tmp_excel, self.session)
        
        products = self.session.query(ProductModel).all()
        self.assertEqual(len(products), 1)
        
        aliases = self.session.query(ProductAliasModel).all()
        self.assertEqual(len(aliases), 1)

if __name__ == '__main__':
    unittest.main()
