# Outfit Products Management System

## Overview

This system combines all outfit products from various sources into a single, comprehensive CSV file for easy management and improved product display in your AI Fashion application.

## Features

✅ **Unified Product Database**: All outfit products from JSON and CSV sources combined into one file  
✅ **Enhanced Recommendations**: Better color matching and personalized suggestions  
✅ **Duplicate Detection**: Automatically removes duplicate products  
✅ **Standardized Format**: Consistent data structure across all products  
✅ **Easy Expansion**: Simple process to add new products from JSON files  

## Files Structure

```
backend/
├── combine_outfit_products.py      # Main script to combine all products
├── add_json_to_csv.py             # Script to add new JSON products
├── processed_data/
│   └── all_combined_outfits.csv   # Combined products file
├── datasets/
│   └── product twirl.json         # Twirl Around World products
└── prods_fastapi/
    └── main.py                    # Updated FastAPI server
```

## Current Product Statistics

- **Total Products**: 243 unique items
- **Unique Brands**: 24 different brands
- **Product Categories**: Apparel, Swimwear, Beach wear, Bikinis, Nightsuits, etc.
- **Data Sources**: Twirl Around World, H&M, Urban Outfitters, and more

## Usage

### 1. Combining All Products (Initial Setup)

```bash
cd backend
python combine_outfit_products.py
```

This will:
- Load products from all JSON and CSV files
- Standardize the data format  
- Remove duplicates
- Create `processed_data/all_combined_outfits.csv`

### 2. Adding New Products from JSON

```bash
cd backend
python add_json_to_csv.py path/to/new_products.json
```

Options:
- `--csv_file`: Specify existing CSV file (default: processed_data/all_combined_outfits.csv)
- `--output_file`: Specify output file (default: same as csv_file)

Example:
```bash
python add_json_to_csv.py datasets/new_collection.json --output_file processed_data/updated_outfits.csv
```

### 3. Running the FastAPI Server

```bash
cd backend/prods_fastapi
uvicorn main:app --reload --port 8000
```

## API Endpoints

### Get All Combined Outfits
```
GET /api/combined-outfits
```

### Get Paginated Outfit Products
```
GET /apparel?page=1&limit=24&color=Blue&color=Black
```

Parameters:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 24, max: 100)
- `gender`: Filter by gender
- `color`: Filter by color (can specify multiple)

### Get Color Recommendations
```
GET /api/color-recommendations?skin_tone=Monk05&hex_color=d7bd96
```

## Data Format

### Combined CSV Structure
```csv
brand,product_name,price,gender,image_url,base_colour,product_type,sub_category,master_category,source
```

### JSON Product Format
```json
{
  "brand": "Brand Name",
  "product_name": "Product Name",
  "price": "$29.99",
  "gender": "Women",
  "image_url": "https://example.com/image.jpg",
  "base_colour": "Blue",
  "product_type": "Dress",
  "sub_category": "Dresses",
  "master_category": "Apparel"
}
```

## Enhanced Features

### 1. Better Product Display
- All products are now displayed instead of just a subset
- Improved pagination with proper total counts
- Better filtering by color, gender, and category

### 2. Improved Recommendations
- Color matching based on skin tone analysis
- Seasonal color palette integration
- Monk skin tone compatibility
- Enhanced scoring algorithm

### 3. Duplicate Management
- Automatic duplicate detection by brand and product name
- Keeps the first occurrence of duplicates
- Maintains data integrity

## Troubleshooting

### Common Issues

1. **No products showing**: Check if `all_combined_outfits.csv` exists in `processed_data/`
2. **Server not starting**: Ensure you're in the correct directory and dependencies are installed
3. **JSON parsing errors**: Verify JSON file format matches expected structure

### File Locations

Make sure these files exist:
- `backend/processed_data/all_combined_outfits.csv`
- `backend/prods_fastapi/processed_data/all_combined_outfits.csv` (copy of above)

### Debugging

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

1. **Add More Products**: Use `add_json_to_csv.py` to add new collections
2. **Enhance Filtering**: Add more filter options (price range, brand, style)
3. **Improve Recommendations**: Implement machine learning for better suggestions
4. **Add Categories**: Expand product categorization for better organization

## Support

For issues or questions:
1. Check the logs for detailed error messages
2. Verify file paths and permissions
3. Ensure all dependencies are installed
4. Test with sample data first

---

**Note**: Always backup your data before running scripts that modify the combined CSV file.
