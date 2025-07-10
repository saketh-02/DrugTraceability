from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch
import json

class DrugTraceabilityTests(TestCase):
    def setUp(self):
        # Initialize the test client
        self.client = Client()
        # Create a test image file
        self.test_image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'',  # empty image content for testing
            content_type='image/jpeg'
        )

    def test_index_page(self):
        """Test if index page loads correctly"""
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'index.html')

    def test_admin_login(self):
        """Test admin login functionality"""
        response = self.client.post(reverse('UserLogin'), {
            'username': 'admin',
            'password': 'admin'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'AdminScreen.html')

    def test_invalid_login(self):
        """Test invalid login attempt"""
        response = self.client.post(reverse('UserLogin'), {
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'Login.html')
        self.assertIn('Invalid login details', str(response.content))

    @patch('DrugTraceApp.views.Web3')
    def test_add_product(self, mock_web3):
        """Test adding a new product"""
        # Mock blockchain interaction
        mock_web3.return_value.eth.accounts = ['0x123']
        mock_web3.return_value.eth.contract.return_value.functions.setTracingData.return_value.transact.return_value = '0x456'
        mock_web3.return_value.eth.wait_for_transaction_receipt.return_value = {'status': 1}
        
        # First login as admin
        self.client.post(reverse('UserLogin'), {
            'username': 'admin',
            'password': 'admin'
        })
        
        # Then try to add a product
        response = self.client.post(reverse('AddProductAction'), {
            't1': 'Test Drug',  # drug name
            't2': '100',        # quantity
            't3': '10.99',      # price
            't4': 'Test Description',  # description
            't5': self.test_image     # image
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'AddProduct.html')

    @patch('DrugTraceApp.views.Web3')
    def test_view_tracing(self, mock_web3):
        """Test viewing tracing details"""
        # Mock blockchain interaction
        mock_web3.return_value.eth.accounts = ['0x123']
        mock_web3.return_value.eth.contract.return_value.functions.getTracingData.return_value.call.return_value = 'addproduct#Test Drug#10.99#100#Test Description#test.jpg#2024-03-20#Production'
        
        response = self.client.get(reverse('ViewTracing'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'ViewTracing.html')
        # Verify that the response contains the table structure
        self.assertIn('Drug Name', str(response.content))
        self.assertIn('Price', str(response.content))
        self.assertIn('Quantity', str(response.content))
        self.assertIn('Current Tracing Info', str(response.content))

    @patch('DrugTraceApp.views.Web3')
    def test_update_tracing(self, mock_web3):
        """Test updating tracing information"""
        # Mock blockchain interaction
        mock_web3.return_value.eth.accounts = ['0x123']
        mock_web3.return_value.eth.contract.return_value.functions.setTracingData.return_value.transact.return_value = '0x456'
        mock_web3.return_value.eth.wait_for_transaction_receipt.return_value = {'status': 1}
        
        # First login as admin
        self.client.post(reverse('UserLogin'), {
            'username': 'admin',
            'password': 'admin'
        })
        
        # Test updating tracing info for a product
        response = self.client.post(reverse('AddTracingAction'), {
            't1': 'Test Drug',          # product name
            't2': 'Production',         # tracing type
            't3': 'In production phase' # tracing status
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'AdminScreen.html')
