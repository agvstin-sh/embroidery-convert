import unittest
import sys
import os
import io
from unittest.mock import MagicMock, patch

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app

class ComprehensiveTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch('app.pyembroidery')
    def test_convert_success_and_extension(self, mock_pyembroidery):
        """Test successful conversion and correct uppercase extension"""
        # Mock pattern
        mock_pattern = MagicMock()
        mock_pyembroidery.read.return_value = mock_pattern
        
        # Mock write to just create the file
        def write_side_effect(pattern, path):
             with open(path, 'wb') as f:
                 f.write(b'converted content')
        mock_pyembroidery.write.side_effect = write_side_effect

        data = {
            'file': (io.BytesIO(b'dummy input'), 'design.exp'),
            'format': 'dst'
        }
        
        response = self.app.post('/convert', data=data, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        
        # Check content
        self.assertEqual(response.data, b'converted content')
        
        # Check extension is uppercase
        cd = response.headers.get('Content-Disposition')
        self.assertIn('filename=design.DST', cd)

    @patch('app.pyembroidery')
    def test_convert_read_error(self, mock_pyembroidery):
        """Test handling of read errors"""
        mock_pyembroidery.read.side_effect = Exception("Read failed")
        
        data = {
            'file': (io.BytesIO(b'bad content'), 'bad.exp'),
            'format': 'dst'
        }
        
        response = self.app.post('/convert', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'Failed to read file', response.data)

    @patch('app.pyembroidery')
    def test_preview_generation(self, mock_pyembroidery):
        """Test preview data generation"""
        # Mock complex pattern structure
        mock_pattern = MagicMock()
        mock_pyembroidery.read.return_value = mock_pattern
        
        # Mock bounds (min_x, min_y, max_x, max_y) -> 100x100mm (1000x1000 units)
        mock_pattern.bounds.return_value = (0, 0, 1000, 1000)
        mock_pattern.count_stitches.return_value = 500
        mock_pattern.count_color_changes.return_value = 1
        
        # Mock threadlist
        thread1 = MagicMock()
        thread1.hex_color.return_value = "#FF0000"
        thread2 = MagicMock()
        thread2.hex_color.return_value = "#00FF00"
        mock_pattern.threadlist = [thread1, thread2]
        
        # Mock stitches
        # (x, y, flags)
        # 0 = Normal, 5 = Color Change
        mock_pattern.stitches = [
            (10, 10, 0),
            (20, 20, 0),
            (0, 0, 5), # Color change
            (30, 30, 0)
        ]

        data = {
            'file': (io.BytesIO(b'preview input'), 'preview.exp')
        }
        
        response = self.app.post('/preview', data=data, content_type='multipart/form-data')
        
        self.assertEqual(response.status_code, 200)
        json_data = response.get_json()
        
        self.assertEqual(json_data['mode'], 'vector')
        self.assertEqual(json_data['stats']['width'], 100.0) # 1000 / 10
        self.assertEqual(json_data['stats']['colors'], 2)
        
        # Check pattern data contains stitches
        self.assertTrue(len(json_data['pattern']) > 0)
        self.assertEqual(json_data['pattern'][0]['color'], '#FF0000')

if __name__ == '__main__':
    unittest.main()
