# Detection Service (Port 8001)
# analyze_photo -> monk_code, confidence, season, undertone, contrast

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from PIL import Image
import io
import sys
from pathlib import Path

# Add backend paths
backend_dir = Path(__file__).parent.parent / "backend"
prods_fastapi_dir = backend_dir / "prods_fastapi"
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(prods_fastapi_dir))

from enhanced_skin_tone_analyzer import EnhancedSkinToneAnalyzer
from database import SessionLocal, SkinToneMapping
from webcolors import hex_to_rgb

app = FastAPI(title="Detection Service", version="1.0.0")

# CORS for microservice communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize analyzer
analyzer = EnhancedSkinToneAnalyzer()

# Monk tone to season mapping
MONK_TO_SEASON = {
    'Monk01': {'season': 'Light Spring', 'undertone': 'warm', 'contrast': 'light'},
    'Monk02': {'season': 'Light Spring', 'undertone': 'warm', 'contrast': 'light'},
    'Monk03': {'season': 'Clear Spring', 'undertone': 'warm', 'contrast': 'medium'},
    'Monk04': {'season': 'Warm Spring', 'undertone': 'warm', 'contrast': 'medium'},
    'Monk05': {'season': 'Soft Autumn', 'undertone': 'neutral', 'contrast': 'medium'},
    'Monk06': {'season': 'Warm Autumn', 'undertone': 'warm', 'contrast': 'medium'},
    'Monk07': {'season': 'Deep Autumn', 'undertone': 'warm', 'contrast': 'high'},
    'Monk08': {'season': 'Deep Winter', 'undertone': 'cool', 'contrast': 'high'},
    'Monk09': {'season': 'Cool Winter', 'undertone': 'cool', 'contrast': 'high'},
    'Monk10': {'season': 'Clear Winter', 'undertone': 'cool', 'contrast': 'high'}
}

def get_monk_skin_tones_from_db():
    """Get Monk skin tones from database."""
    try:
        db = SessionLocal()
        mappings = db.query(SkinToneMapping).all()
        monk_tones = {}
        for mapping in mappings:
            monk_tones[f'Monk {mapping.monk_tone[-2:]}'] = mapping.hex_code
        db.close()
        return monk_tones
    except Exception as e:
        print(f"Database error: {e}")
        # Fallback tones
        return {
            'Monk 01': '#f6ede4', 'Monk 02': '#f3e7db', 'Monk 03': '#f7ead0',
            'Monk 04': '#eadaba', 'Monk 05': '#d7bd96', 'Monk 06': '#a07e56',
            'Monk 07': '#825c43', 'Monk 08': '#604134', 'Monk 09': '#3a312a',
            'Monk 10': '#292420'
        }

MONK_SKIN_TONES = get_monk_skin_tones_from_db()

@app.get("/")
def root():
    return {"service": "Detection Service", "status": "running", "port": 8001}

@app.get("/health")
def health():
    return {"status": "healthy", "service": "detection"}

@app.post("/analyze_photo")
async def analyze_photo(file: UploadFile = File(...)):
    """
    Analyze uploaded photo and return monk_code, confidence, season, undertone, contrast
    """
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")

        # Read image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image_array = np.array(image)

        # Analyze with enhanced analyzer
        try:
            result = analyzer.analyze_skin_tone(image_array, MONK_SKIN_TONES)
            
            if result['success']:
                monk_code = result['monk_skin_tone']
                confidence = result['confidence']
                
                # Get season classification
                season_info = MONK_TO_SEASON.get(monk_code, {
                    'season': 'Soft Autumn', 
                    'undertone': 'neutral', 
                    'contrast': 'medium'
                })
                
                return {
                    "monk_code": monk_code,
                    "confidence": confidence,
                    "season": season_info['season'],
                    "undertone": season_info['undertone'],
                    "contrast": season_info['contrast'],
                    "monk_hex": result.get('monk_hex', '#d7bd96'),
                    "derived_hex": result.get('derived_hex_code', '#d7bd96'),
                    "success": True
                }
            else:
                # Fallback analysis
                return fallback_analysis(image_array)
                
        except Exception as analyzer_error:
            print(f"Enhanced analyzer failed: {analyzer_error}")
            return fallback_analysis(image_array)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

def fallback_analysis(image_array):
    """Simple fallback skin tone analysis"""
    try:
        h, w = image_array.shape[:2]
        center_region = image_array[h//4:3*h//4, w//4:3*w//4]
        avg_color = np.mean(center_region.reshape(-1, 3), axis=0)
        
        # Find closest Monk tone
        min_distance = float('inf')
        closest_monk = "Monk05"
        
        for monk_name, hex_color in MONK_SKIN_TONES.items():
            try:
                monk_rgb = np.array(hex_to_rgb(hex_color))
                distance = np.sqrt(np.sum((avg_color - monk_rgb) ** 2))
                
                if distance < min_distance:
                    min_distance = distance
                    closest_monk = f"Monk{monk_name.split()[1].zfill(2)}"
            except:
                continue
        
        season_info = MONK_TO_SEASON.get(closest_monk, {
            'season': 'Soft Autumn', 
            'undertone': 'neutral', 
            'contrast': 'medium'
        })
        
        return {
            "monk_code": closest_monk,
            "confidence": 0.7,
            "season": season_info['season'],
            "undertone": season_info['undertone'],
            "contrast": season_info['contrast'],
            "monk_hex": MONK_SKIN_TONES.get(f"Monk {closest_monk[-2:]}", "#d7bd96"),
            "derived_hex": f"#{int(avg_color[0]):02x}{int(avg_color[1]):02x}{int(avg_color[2]):02x}",
            "success": True,
            "fallback": True
        }
        
    except Exception as e:
        return {
            "monk_code": "Monk05",
            "confidence": 0.5,
            "season": "Soft Autumn",
            "undertone": "neutral",
            "contrast": "medium",
            "monk_hex": "#d7bd96",
            "derived_hex": "#d7bd96",
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
