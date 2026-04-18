from src.infrastructure.scrapers.base import ScrapedOffer
from src.infrastructure.scrapers.pipeline import ScrapingPipeline
from loguru import logger
import unittest
from unittest.mock import MagicMock, patch

class TestPipelineHardening(unittest.TestCase):
    def test_standardization(self):
        # Create a ScrapedOffer (Pydantic v2)
        offer = ScrapedOffer(
            product_name="Test Product",
            price=10.0,
            url="http://example.com/item1",
            shop_name="Test Shop"
        )
        
        # Create a pipeline with no scrapers (we only want to test update_database logic)
        pipeline = ScrapingPipeline([])
        
        # Mock SessionCloud to avoid DB connection
        with patch('src.infrastructure.database_cloud.SessionCloud') as mock_session:
            # We also need to mock BackupManager to avoid writing files if we want a clean test,
            # but here we WANT to see if it receives the right data.
            with patch('src.core.backup_manager.BackupManager.save_raw_snapshot') as mock_save:
                try:
                    pipeline.update_database([offer])
                except Exception as e:
                    # It might fail later on DB calls, but we check the mock_save call
                    print(f"Caught expected DB failure: {e}")
                
                # Verify BackupManager received a dict, not a ScrapedOffer object
                args, kwargs = mock_save.call_args
                received_offers = args[1]
                
                print(f"Type of first item sent to backup: {type(received_offers[0])}")
                self.assertIsInstance(received_offers[0], dict)
                self.assertEqual(received_offers[0]['product_name'], "Test Product")
                print("✅ Verification Successful: ScrapedOffer correctly converted to dict.")

if __name__ == "__main__":
    unittest.main()
