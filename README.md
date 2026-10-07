# 🌾 AI-Based Crop Waste Value Finder

An intelligent, full-stack web application designed for farmers to evaluate post-harvest agricultural residues (paddy straw, maize stalks, cotton stalks, sugarcane trash, coconut coir, etc.), calculate approximate commercial values, discover optimal recycling/conversion pathways, measure educational environmental pollution reduction indicators, and connect with potential regional buyers instead of open-field burning.

---

## 📋 Table of Contents
1. [Project Overview & Objectives](#-project-overview--objectives)
2. [Key Features](#-key-features)
3. [Technology Stack](#-technology-stack)
4. [Project Architecture & Design Diagrams](#-project-architecture--design-diagrams)
   - [System Architecture Description & Diagram](#system-architecture)
   - [Entity-Relationship (ER) Diagram Description](#entity-relationship-er-diagram)
   - [Use-Case Diagram Description](#use-case-diagram)
5. [Installation & Setup Instructions](#-installation--setup-instructions)
6. [API & AI Configuration](#-api--ai-configuration)
7. [Demo Login Credentials](#-demo-login-credentials)
8. [Step-by-Step College Demonstration Flow](#-step-by-step-college-demonstration-flow)
9. [Automated Testing](#-automated-testing)
10. [Limitations](#-limitations)
11. [Future Scope](#-future-scope)
12. [Comprehensive Viva Voce Questions & Answers](#-comprehensive-viva-voce-questions--answers)

---

## 🎯 Project Overview & Objectives

### The Problem
In India and several agrarian economies, post-harvest crop residue disposal is a critical challenge. Due to narrow turnaround windows between crop rotations, lack of knowledge about alternative uses, and absent localized buyer networks, farmers often resort to open-field burning. This practice causes:
- Severe seasonal air pollution and hazardous atmospheric smog (elevated particulate matter $\text{PM}_{2.5}$ and $\text{PM}_{10}$).
- Destruction of beneficial soil organic carbon, mycorrhizae, and earthworms.
- Direct loss of supplementary economic income for rural households.

### The Solution
**Crop Waste Value Finder** bridges this gap by providing a farmer-friendly web portal that transforms crop residue from a disposal burden into an economic asset:
- **Agronomic AI Analysis**: Automatically calculates suitability scores across multiple conversion avenues (Cattle roughage, mushroom cultivation, biomass briquettes/pellets, compost).
- **Realistic Valuation Bounds**: Generates approximate price estimations with explicit disclaimers preventing market confusion.
- **Regional Buyer Directory & Interactive Map**: Visualizes nearby demo buyers using OpenStreetMap / Leaflet, calculating distance using the spherical Haversine formula.
- **Multilingual Waste Assistant**: A chatbot capable of communicating in English, Telugu (తెలుగు), and Telugu+English.
- **Educational Environmental Calculator**: Demonstrates quantitative savings in carbon emissions and trees equivalent when burning is averted.

---

## ✨ Key Features

1. **Farmer Authentication & Profiles**:
   - Secure registration with mobile, email, and farm location.
   - Password hashing utilizing Werkzeug (`scrypt`/`pbkdf2:sha256`).
   - Session-based authorization with role separation (Farmer & Admin).

2. **Farmer Dashboard**:
   - High-level metric cards: Total records logged, cumulative waste tonnage, potential value range, and recommended application count.
   - Quick navigation shortcuts designed with large tactile buttons.
   - Recent residue submission activity log.

3. **Crop Waste Input Form**:
   - Supported crops: Paddy, Maize, Cotton, Sugarcane, Wheat, Groundnut, Coconut, and Other.
   - Dynamic residue suggestion dropdown with custom override.
   - Multi-unit conversion support (`kg`, `quintal`, `ton`).
   - Optional photo upload with size limit validation (8MB) and secure filenames.

4. **Intelligent AI Recommendation Engine**:
   - Dual-engine architecture:
     - **OpenAI API Integration**: Structured JSON prompts analyzing crop, quantity, and location.
     - **Built-in Agronomic Knowledge Engine**: Deterministic, offline fallback model calibrated on Indian Council of Agricultural Research (ICAR) guidelines.
   - Multi-application recommendation scores displayed as visual progress bars (e.g., Animal Feed: 85%, Compost: 70%, Biomass: 60%).
   - Explicit disclaimer: *"Estimated value only. Actual price may vary depending on quality, location, demand, and buyer."*

5. **Potential Buyer Directory**:
   - Filter by crop type, buyer category, and location.
   - Buyer categories: Cattle-feed businesses, Compost producers, Biomass companies, Mushroom farms, Paper/packaging, Biofuel users, Organic farming collectives.
   - Simulated contact dialog with demo indicators.

6. **Nearby Buyer Map (OpenStreetMap + Leaflet.js)**:
   - Visualizes farmer location pin (green tractor) alongside regional buyer pins (blue industry).
   - Distance calculation and popups with contact and capacity details.
   - Fallback accessible table for low-bandwidth or offline environments.

7. **Multilingual "Waste Assistant" Chatbot**:
   - Switch between **English**, **Telugu (తెలుగు)**, and **Telugu + English**.
   - Handles queries regarding silage making, mushroom beds, biomass sales, and smoke prevention.

8. **Environmental Impact Calculator**:
   - Computes open-burning avoidance indicators ($\text{CO}_2$, $\text{CO}$, $\text{PM}_{2.5}$, and tree-absorption equivalence).
   - Explicitly marked as an *"Estimated educational indicator"*.

9. **Administrator Dashboard**:
   - Interactive charts powered by Chart.js (Crop volume distribution, common waste types, top recommended uses).
   - Full CRUD capability over demo buyers, plus inspection of all farmer accounts and submissions.

---

## 🛠 Technology Stack

| Layer | Technologies Used |
|---|---|
| **Frontend** | HTML5, CSS3, JavaScript (ES6+), Bootstrap 5.3, FontAwesome 6, Leaflet.js, Chart.js |
| **Backend** | Python 3.10+, Flask, Werkzeug, Jinja2 |
| **Database** | SQLite3 (Zero-configuration, lightweight relational database) |
| **AI / NLP** | OpenAI API (`gpt-3.5-turbo` JSON mode) with built-in fallback Agronomic Rule Engine |
| **Mapping / GIS** | OpenStreetMap, Leaflet.js, Haversine Great-Circle Distance Algorithm |
| **Configuration** | `python-dotenv` for environment variable isolation |

---

## 📐 Project Architecture & Design Diagrams

### System Architecture
The application follows a clean 3-tier **Model-View-Service-Controller (MVSC)** architecture:

```
[ Farmer Browser / Client UI ]
     │ (HTML5, Bootstrap 5, Leaflet.js, Chart.js)
     ▼
[ Flask Application (Controller & Routes: app.py) ]
     │
     ├──► [ Auth & Security Layer ] (Werkzeug Password Hash, Sessions)
     │
     ├──► [ Services Layer ]
     │      ├── AIService (OpenAI API + Intelligent Fallback)
     │      ├── RecommendationService (Agronomic profiles & Scoring)
     │      └── BuyerService (Haversine Distance & Spatial Markers)
     │
     ├──► [ Models Layer ]
     │      ├── UserModel (Farmer accounts)
     │      ├── WasteModel (Crop residue submissions)
     │      ├── RecommendationModel (Scores & valuation)
     │      └── BuyerModel (Directory & Admin CRUD)
     │
     └──► [ SQLite Database ] (database.db)
```

### Entity-Relationship (ER) Diagram Description
The SQLite relational database consists of five normalized tables:

1. **`users` Table**:
   - `id` (INTEGER, Primary Key, Auto-increment)
   - `name` (TEXT)
   - `mobile` (TEXT, Unique)
   - `email` (TEXT, Unique)
   - `password_hash` (TEXT)
   - `village` (TEXT), `district` (TEXT), `state` (TEXT)
   - `created_at` (TIMESTAMP)

2. **`waste_records` Table**:
   - `id` (INTEGER, Primary Key, Auto-increment)
   - `user_id` (INTEGER, Foreign Key $\rightarrow$ `users.id`)
   - `crop_name` (TEXT)
   - `waste_type` (TEXT)
   - `quantity` (REAL)
   - `unit` (TEXT: 'kg', 'quintal', 'ton')
   - `village`, `district`, `state` (TEXT)
   - `harvest_date` (TEXT)
   - `storage_condition` (TEXT)
   - `image` (TEXT, filename in uploads)
   - `created_at` (TIMESTAMP)

3. **`recommendations` Table**:
   - `id` (INTEGER, Primary Key, Auto-increment)
   - `waste_record_id` (INTEGER, Foreign Key $\rightarrow$ `waste_records.id`)
   - `recommended_use` (TEXT)
   - `estimated_min_value` (REAL)
   - `estimated_max_value` (REAL)
   - `explanation` (TEXT)
   - `environmental_benefit` (TEXT)
   - `scores_json` (TEXT, JSON string of scores)
   - `created_at` (TIMESTAMP)

4. **`buyers` Table**:
   - `id` (INTEGER, Primary Key, Auto-increment)
   - `business_name` (TEXT)
   - `category` (TEXT)
   - `waste_types` (TEXT)
   - `village`, `district`, `state` (TEXT)
   - `latitude` (REAL), `longitude` (REAL)
   - `capacity` (TEXT)
   - `contact` (TEXT)
   - `is_demo` (INTEGER, default 1)

5. **`admin` Table**:
   - `id` (INTEGER, Primary Key, Auto-increment)
   - `username` (TEXT, Unique)
   - `password_hash` (TEXT)
   - `created_at` (TIMESTAMP)

### Use-Case Diagram Description
- **Actor 1: Farmer**
  - Register & Authenticate.
  - Log Crop Waste (crop type, quantity, storage, location, photo).
  - Review AI Valuation & Multi-use Recommendation Scores.
  - Browse Matching Buyers & Inspect Interactive Map.
  - Interact with Multilingual "Waste Assistant" Chatbot.
  - Calculate Avoided Environmental Emissions.
  - View Historical Submission Reports.
- **Actor 2: Administrator**
  - Log into Admin Control Panel.
  - View Aggregated Platform Statistics & Charts (Chart.js).
  - Inspect Registered Farmers & Waste Logs.
  - Add, Update, or Delete Potential Demo Buyers.

---

## 💻 Installation & Setup Instructions

### Prerequisites
- Python 3.10, 3.11, 3.12, 3.13, or 3.14 installed on your machine.
- Git (optional).

### Step 1: Clone or Navigate to the Project Directory
```bash
cd "c:\Users\Karthik\OneDrive\Desktop\project"
```

### Step 2: Create and Activate a Virtual Environment
**On Windows (PowerShell / Command Prompt):**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

**On Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Required Packages
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Copy `.env.example` to `.env` (already created with defaults):
```bash
# In .env:
SECRET_KEY=crop-waste-dev-secret-key-2026
FLASK_ENV=development
PORT=5000
# Optional: Provide OpenAI API Key if you wish to use live OpenAI queries
OPENAI_API_KEY=
```

### Step 5: Initialize the Database (Automatic or Manual)
The database auto-initializes upon launching the app. You can also re-seed fresh demo data at any time:
```bash
python database/init_db.py
```

### Step 6: Run the Application
```bash
python app.py
```
Open your web browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🔑 Demo Login Credentials

For testing and college presentation, the database comes pre-seeded with verified test accounts:

| Role | Username / Identifier | Password | Access Details |
|---|---|---|---|
| **Demo Farmer** | `farmer@demo.org` *(or mobile `9876543210`)* | `farmer123` | Full Farmer Dashboard, History, Add Waste |
| **Administrator** | `admin` | `admin123` | Admin Analytics, User Inspection, Buyer CRUD |

*Tip: On the login page, you can click the **Autofill Demo Farmer** or **Autofill Demo Admin** button to populate credentials instantly.*

---

## 🚀 Step-by-Step College Demonstration Flow

Follow this exact sequence for an end-to-end project viva or demonstration:

1. **Launch**: Start `python app.py` and open `http://127.0.0.1:5000`.
2. **Landing Page**:
   - Showcase the hero section: *"Turn Crop Waste Into Value 🌾"*.
   - Point out the Problem (stubble burning, air pollution) and Solution cards.
3. **Farmer Login / Registration**:
   - Click **Farmer Login**, click **Autofill Demo Farmer**, and hit **Log In**.
   - (Or click **Register Free** to register a new farmer).
4. **Farmer Dashboard**:
   - Observe the 4 metric cards: Total Waste Records, Waste Quantity, Estimated Value Range, and Optimal Applications.
5. **Add Waste Entry**:
   - Click **Add Waste & Find Value**.
   - Select Crop: `Paddy`. Notice that the suggested waste type dropdown immediately auto-populates `Paddy Straw`.
   - Enter Quantity: `500`, Unit: `kg`.
   - Observe that the location is auto-filled (`Tenali`, `Guntur`).
   - Click **Find Value**.
6. **AI Valuation & Recommendation Report**:
   - Showcase the **Best Recommended Use** card (`Animal feed (Enriched Roughage)`).
   - Point out the **Recommendation Suitability Scores** with colorful progress bars (Animal feed 85%, Compost 70%, Biomass briquettes 60%, Mushroom cultivation 55%).
   - Highlight the **Estimated Value**: ₹3 – ₹6 per kg (Total batch: ₹1,500 – ₹3,000).
   - Read the prominent legal/market disclaimer: *"Estimated value only. Actual price may vary depending on quality, location, demand, and buyer."*
   - Review the **Environmental Impact** indicators: ~730 kg $\text{CO}_2$ avoided and 33 trees equivalent.
7. **Find Matching Buyers**:
   - Click the **Find Matching Buyers** button.
   - Filter by Crop (`Paddy`) and District (`Guntur`).
   - Inspect the buyer cards with **Demo Buyer** badges, distance calculation (e.g. `14.2 km away`), capacity, and click **Contact Buyer** to view the simulated procurement modal.
8. **Nearby Buyer Map**:
   - Click **Nearby Map** in the navbar.
   - Observe the OpenStreetMap interface with the **Farmer Location Pin (Green Tractor)** and **Buyer Pins (Blue Factory)**.
   - Click pins to show interactive popups. Show the accessible fallback list below the map.
9. **Waste Assistant Chatbot**:
   - Click **AI Assistant** in the navbar.
   - Switch language to **English**, click *"What can I do with paddy straw?"* and inspect the response.
   - Switch language to **తెలుగు (Telugu)** or **Telugu + English** and ask *"Can this waste be used as animal feed?"*. Show the localized agronomic advice.
10. **Environmental Impact Calculator**:
    - Open **Impact** in navbar.
    - Enter `2.5 tons` of maize or paddy. Show the dynamic calculation of $\text{CO}_2$, $\text{CO}$, $\text{PM}_{2.5}$, and trees equivalence labeled as an *"Estimated educational indicator"*.
11. **My Waste Records History**:
    - Click **History** in navbar to see the saved record history with full viewing/deletion capabilities.
12. **Admin Panel**:
    - Click **Admin Portal** in the footer, log in as `admin` / `admin123`.
    - Present the **Chart.js visualizations**: Waste Quantity by Crop, Common Waste Types, and Top Recommended Applications.
    - Demonstrate adding or updating a demo buyer in **Manage Buyers**.

---

## 🧪 Automated Testing

The project includes an automated test suite verifying all 8 major functional modules:
```bash
python test_app.py
```
Expected output:
```
Ran 8 tests in 1.327s
OK
```

---

## ⚠️ Limitations

1. **Estimated vs. Real-Time Prices**: The price estimates (e.g., ₹3–₹6/kg) are domain-calibrated benchmark estimates and not live electronic spot prices from a commodity exchange.
2. **Prototype Demo Buyers**: All buyer entries in SQLite are simulated demo accounts created for academic illustration; real commercial contracts require verified KYC buyer onboarding.
3. **Open-Burning Environmental Indicators**: Calculated carbon and particulate metrics are benchmark educational estimates derived from ICAR/IPCC empirical averages rather than real-time field flue gas sensors.
4. **Internet Dependency for Cloud Maps**: Leaflet tiles and OpenAI API require internet connectivity; if offline, the app utilizes its built-in Rule Engine and the accessible tabular fallback directory.

---

## 🔮 Future Scope

1. **Real-Time Ag-Market Price API**: Integration with government portals like **e-NAM (National Agriculture Market)** and **Agmarknet** for daily spot prices.
2. **KYC Verified Buyer Accounts**: Allow industrial buyers and cattle-feed companies to create verified purchasing accounts with bidding capabilities.
3. **WhatsApp / SMS Gateway**: Automated SMS notifications and WhatsApp alerts when a new buyer within a 25 km radius posts a residue procurement requirement.
4. **Computer Vision Residue Identification**: Image-based waste classification utilizing convolutional neural networks (CNNs) to determine crop moisture and baling quality from mobile camera photos.
5. **Government CRM Scheme Integration**: Linking farmers to regional custom hiring centers (CHCs) for subsidized machinery (balers, happy seeders, rotavators).
6. **Smart IoT Storage Sensors**: LoRa/IoT moisture probes inside storage sheds to prevent spontaneous combustion and fungal decay.

---

## 🎓 Comprehensive Viva Voce Questions & Answers

### Q1: What is the primary objective of this project?
**Answer:** The objective is to develop a web-based decision support system for farmers that prevents open-field crop residue burning by using AI and agricultural knowledge models to classify waste, recommend the most viable economic uses (animal feed, compost, mushroom substrate, biomass fuel), provide estimated value ranges, and connect farmers with regional buyers.

### Q2: Why did you choose Flask and SQLite for this project?
**Answer:** 
- **Flask** is a lightweight, modular Python microframework that offers great architectural flexibility, rapid request-response handling, and straightforward integration with AI libraries and external APIs without the monolithic bloat of larger frameworks.
- **SQLite** is serverless, self-contained, and requires zero administrative setup, making it ideal for prototyping, offline-tolerant execution, and academic demonstrations while still supporting standard SQL ACID transactions and foreign key constraints.

### Q3: How does the AI recommendation engine work when an OpenAI API key is not available?
**Answer:** The system uses a **Graceful Degradation Architecture**. If the OpenAI API key is absent or network requests fail, the application seamlessly falls back to the built-in `RecommendationService` Agronomic Knowledge Engine. This engine is encoded with multi-factor scoring algorithms and empirical ICAR crop profiles (covering paddy, maize, cotton, sugarcane, wheat, groundnut, coconut) that compute suitability scores and price ranges deterministically.

### Q4: How is distance calculated between the farmer and buyers on the map?
**Answer:** The system uses the **Haversine Formula**, which computes the great-circle distance between two pairs of latitude and longitude coordinates over the Earth's spherical surface:
$$d = 2r \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$
where $r = 6371\text{ km}$ is the mean radius of Earth.

### Q5: How do you secure farmer passwords in the database?
**Answer:** Passwords are never stored in plaintext. They are hashed using Werkzeug's `generate_password_hash()`, which implements salted cryptographic password hashing (`scrypt` / `pbkdf2:sha256`). When logging in, `check_password_hash()` compares the hashed value securely against timing attacks.

### Q6: Why is there an explicit disclaimer regarding estimated waste prices?
**Answer:** Agricultural residue prices are not centrally regulated like Minimum Support Prices (MSP) for grain. Crop waste price depends heavily on moisture percentage, whether it is loose or baled, seasonal supply-demand dynamics, and haulage/transport costs. Hence, presenting estimated values as guaranteed market prices would mislead farmers. The application prominently displays: *"Estimated value only. Actual price may vary depending on quality, location, demand, and buyer."*

### Q7: How does the Multilingual Chatbot handle Telugu queries?
**Answer:** The `Waste Assistant` chatbot provides a language selection toggle (`English`, `తెలుగు`, `Telugu + English`). In offline/mock mode, an intent parser analyzes keywords (such as `వరి` for paddy, `మొక్కజొన్న` for maize, `మేత` for fodder, `కాల్చ` for burning) and retrieves contextual agronomic guidance in clear Telugu script or bilingual text. If an OpenAI API key is supplied, a system instruction enforces responses in the specified Indian regional dialect.

### Q8: What environmental metrics are calculated, and what is their source?
**Answer:** The environmental impact calculator estimates the emissions avoided by not burning residue:
- $\approx 1,460\text{ kg } \text{CO}_2\text{ equivalent}$ avoided per metric ton of residue.
- $\approx 60\text{ kg } \text{CO}$ avoided.
- $\approx 3.2\text{ kg } \text{PM}_{2.5}$ fine particulate matter avoided.
- Tree absorption equivalence ($\approx 22\text{ kg } \text{CO}_2/\text{year}$ per mature tree).
These values are benchmark empirical averages from agricultural residue burning studies by the Indian Agricultural Research Institute (IARI) and IPCC guidelines, labeled explicitly as an *"Estimated educational indicator"*.

---

## 👨‍💻 Author & Academic Attribution
- **Project**: AI-Based Crop Waste Value Finder
- **Target Audience**: Indian Farming Communities & Bio-economy Aggregators
- **Year**: 2026
