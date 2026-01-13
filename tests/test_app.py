import unittest
import sys
import os
import io

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class EmbroideryAppTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_index_route(self):
        """Test if the home page loads successfully"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)

    def test_convert_no_file(self):
        """Test conversion without sending a file"""
        response = self.app.post('/convert', data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No file part', response.data)

    def test_convert_no_format(self):
        """Test conversion without specifying a format"""
        data = {
            'file': (io.BytesIO(b'dummy content'), 'design.pes')
        }
        response = self.app.post('/convert', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No target format specified', response.data)

if __name__ == '__main__':
    unittest.main()
