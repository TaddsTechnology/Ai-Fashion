# HueMatch: Personalized Color Recommendations

HueMatch is an AI-powered application that analyzes your skin tone and provides personalized color recommendations for clothing, makeup, and accessories. The application uses the Monk Skin Tone (MST) scale to identify your skin tone and suggests colors that complement your natural complexion.

## Features
- **Skin Tone Analysis**: Upload a photo to analyze your skin tone using AI.
- **Personalized Color Palettes**: Receive color recommendations based on your skin tone.
- **Makeup Recommendations**: Discover makeup products that match your skin tone.
- **Outfit Suggestions**: Browse outfit ideas with colors that complement your complexion.
- **Seasonal Color Analysis**: Identify your seasonal color type (Spring, Summer, Autumn, Winter).

## Table of Contents
1. [Installation](#installation)
2. [Getting Started](#getting-started)
3. [Project Structure](#project-structure)
4. [Backend API](#backend-api)
5. [Frontend](#frontend)
6. [Data Sources](#data-sources)
7. [Troubleshooting](#troubleshooting)
8. [Contributing](#contributing)
9. [License](#license)
10. [Acknowledgements](#acknowledgements)

---

## Installation

### Prerequisites
- Python 3.8+
- Node.js 14+
- npm or yarn

### Backend Setup
1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/huematch.git
   cd huematch
   ```
2. Create a Python virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install backend dependencies:
   ```sh
   pip install -r backend/prods_fastapi/requirements.txt
   ```
4. Ensure you have the necessary data files in `backend/processed_data/`:
   - `seasonal_palettes.json`
   - `sample_makeup_products.csv`
   - `all_makeup_products.csv`
   - Other product data files

### Frontend Setup
1. Navigate to the frontend directory:
   ```sh
   cd frontend
   ```
2. Install frontend dependencies:
   ```sh
   yarn install  # or npm install
   ```

---

## Getting Started

### Starting the Backend Server
1. Navigate to the FastAPI backend directory:
   ```sh
   cd backend/prods_fastapi
   ```
2. Start the FastAPI server:
   ```sh
   python -m uvicorn main:app --reload
   ```
3. The backend server will run at `http://localhost:8000`.
4. API documentation is available at:
   - **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### Starting the Frontend Development Server
1. Navigate to the frontend directory:
   ```sh
   cd frontend
   ```
2. Start the development server:
   ```sh
   yarn dev  # or npm run dev
   ```
3. The frontend will be available at `http://localhost:5173`.

---

## Project Structure
```
huematch/
├── backend/
│   ├── prods_fastapi/
│   │   ├── main.py            # FastAPI application
│   │   ├── color_utils.py     # Color utilities
│   │   └── requirements.txt   # Backend dependencies
│   └── processed_data/        # Data files
│       ├── seasonal_palettes.json
│       ├── sample_makeup_products.csv
│       ├── all_makeup_products.csv
│       └── ...
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   ├── utils/             # Utility functions
│   │   ├── lib/               # Library code
│   │   └── App.tsx            # Main application component
│   ├── public/                # Static assets
│   ├── package.json           # Frontend dependencies
│   └── vite.config.ts         # Vite configuration
└── README.md                  # Project documentation
```

---

## Backend API

### Color Recommendations
- **GET /api/color-recommendations**: Get color recommendations based on skin tone.
  - Query parameters:
    - `skin_tone`: Skin tone category (e.g., 'Monk03', 'Clear Spring')
    - `hex_color`: Hex color code of the skin tone (e.g., '#f7ead0')

### Makeup Products
- **GET /data/**: Get makeup products with pagination and filtering.
  - Query parameters:
    - `mst`: Monk Skin Tone (e.g., 'Monk03')
    - `ogcolor`: Original color in hex (without `#`)
    - `page`: Page number (starts at 1)
    - `limit`: Number of items per page (max 100)
    - `product_type`: Filter by product type (comma-separated for multiple types)

### Outfit Recommendations
- **GET /apparel**: Get outfit recommendations with pagination.
  - Query parameters:
    - `gender`: Filter by gender (e.g., 'Men', 'Women')
    - `color`: Filter by one or more colors (e.g., 'Blue', 'Black')
    - `page`: Page number (starts at 1)
    - `limit`: Number of items per page (max 100)

---

## Data Sources
HueMatch uses the following data sources:
- **Monk Skin Tone Scale**: A 10-point skin tone scale developed by Ellis Monk.
- **Seasonal Color Analysis**: A theory that categorizes individuals into seasonal types.
- **Product Data**: Sample makeup and clothing product datasets.

---

## Troubleshooting
### Common Issues
- **Backend server won't start**
  - Ensure Python 3.8+ is installed.
  - Check that all dependencies are installed: `pip install -r requirements.txt`.
  - Verify that the required data files exist in `backend/processed_data/`.
- **Frontend development server won't start**
  - Ensure Node.js 14+ is installed.
  - Check that all dependencies are installed: `yarn install`.
  - Verify that `vite.config.ts` is properly configured.
- **API connection errors**
  - Ensure the backend server is running at `http://localhost:8000`.
  - Check for CORS issues in the browser console.

---

## Contributing
We welcome contributions! Follow these steps:
1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature-name`.
3. Commit your changes: `git commit -m 'Add some feature'`.
4. Push to the branch: `git push origin feature/your-feature-name`.
5. Open a pull request.

---

## License
This project is licensed under the MIT License - see the LICENSE file for details.

---

## Acknowledgements
- Ellis Monk for the Monk Skin Tone Scale.
- The seasonal color analysis community for insights.
- All contributors who have improved this project!

For support, open an issue on GitHub or contact us at support@huematch.example.com.

