import unittest
import json
from app import app
from database.init_db import init_db

class CropWasteValueFinderTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Initialize fresh database state
        init_db(force_recreate=True)
        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False

    def setUp(self):
        self.client = app.test_client()

    def test_01_home_page(self):
        """Test landing page loads properly."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Turn Crop Waste Into Value", response.data)
        self.assertIn(b"Find Waste Value", response.data)

    def test_02_farmer_login_demo(self):
        """Test logging in with demo credentials."""
        response = self.client.post("/login", data={
            "identifier": "farmer@demo.org",
            "password": "farmer123"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Ramesh Kumar", response.data)
        self.assertIn(b"Dashboard", response.data)

    def test_03_farmer_registration(self):
        """Test registering a new farmer."""
        response = self.client.post("/register", data={
            "name": "Suresh Reddy",
            "mobile": "9123456789",
            "email": "suresh@kisan.org",
            "password": "password123",
            "confirm_password": "password123",
            "village": "Mangalagiri",
            "district": "Guntur",
            "state": "Andhra Pradesh"
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Registration successful", response.data)

    def test_04_add_waste_and_ai_valuation(self):
        """Test College Demo Flow: Adding Paddy Straw 500kg and getting AI analysis."""
        # Log in first
        self.client.post("/login", data={
            "identifier": "farmer@demo.org",
            "password": "farmer123"
        })

        # Submit waste form
        response = self.client.post("/add-waste", data={
            "crop_name": "Paddy",
            "waste_type": "Paddy Straw",
            "quantity": "500",
            "unit": "kg",
            "village": "Tenali",
            "district": "Guntur",
            "state": "Andhra Pradesh",
            "harvest_date": "2026-10-01",
            "storage_condition": "Dry covered shed"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        # Should redirect to analysis page
        self.assertIn(b"Paddy Straw", response.data)
        self.assertIn(b"BEST RECOMMENDED USE", response.data)
        self.assertIn(b"Animal feed", response.data)
        self.assertIn(b"Estimated value only", response.data)
        self.assertIn(b"Recommendation Suitability Scores", response.data)
        self.assertIn(b"Environmental Impact of Avoiding Waste Burning", response.data)

    def test_05_buyer_finder_and_map_api(self):
        """Test buyer directory and map markers API."""
        # 1. Buyer directory filter
        response = self.client.get("/buyers?crop=Paddy&location=Guntur")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Demo Buyer", response.data)

        # 2. Map data API
        api_res = self.client.get("/api/map-data?location=Guntur")
        self.assertEqual(api_res.status_code, 200)
        data = json.loads(api_res.data)
        self.assertIn("farmer", data)
        self.assertIn("buyers", data)
        self.assertGreater(len(data["buyers"]), 0)

    def test_06_ai_assistant_multilingual(self):
        """Test Waste Assistant chat API in English, Telugu, and Telugu+English."""
        # English
        res_en = self.client.post("/api/chat", json={
            "message": "What can I do with paddy straw?",
            "language": "en"
        })
        self.assertEqual(res_en.status_code, 200)
        data_en = json.loads(res_en.data)
        self.assertIn("response", data_en)
        self.assertTrue(len(data_en["response"]) > 20)

        # Telugu
        res_te = self.client.post("/api/chat", json={
            "message": "వరి గడ్డితో ఏం చేయవచ్చు?",
            "language": "te"
        })
        self.assertEqual(res_te.status_code, 200)
        data_te = json.loads(res_te.data)
        self.assertIn("వరి", data_te["response"])

        # Telugu + English (Tanglish)
        res_te_en = self.client.post("/api/chat", json={
            "message": "Can I use maize as animal feed?",
            "language": "te-en"
        })
        self.assertEqual(res_te_en.status_code, 200)
        data_te_en = json.loads(res_te_en.data)
        self.assertIn("response", data_te_en)

    def test_07_environmental_impact_calculator(self):
        """Test Environmental Impact calculation."""
        response = self.client.post("/impact", data={
            "crop": "Paddy",
            "quantity": "2",
            "unit": "ton"
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"CO2 Prevented", response.data)
        self.assertIn(b"Estimated educational indicator", response.data)

    def test_08_admin_flow(self):
        """Test Admin login, dashboard analytics, and buyer management."""
        # Login admin
        admin_res = self.client.post("/admin/login", data={
            "username": "admin",
            "password": "admin123"
        }, follow_redirects=True)
        self.assertEqual(admin_res.status_code, 200)
        self.assertIn(b"Administrator Control Center", admin_res.data)

        # Users list
        users_res = self.client.get("/admin/users")
        self.assertEqual(users_res.status_code, 200)
        self.assertIn(b"Registered Farmers Directory", users_res.data)

        # Waste list
        waste_res = self.client.get("/admin/waste")
        self.assertEqual(waste_res.status_code, 200)
        self.assertIn(b"All Crop Waste Records", waste_res.data)

        # Buyers management
        buyers_res = self.client.get("/admin/buyers")
        self.assertEqual(buyers_res.status_code, 200)
        self.assertIn(b"Manage Potential Demo Buyers", buyers_res.data)

if __name__ == "__main__":
    unittest.main()
