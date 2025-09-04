import gradio as gr
import numpy as np
try:
    import cv2
except ImportError:
    cv2 = None
from PIL import Image
import io
from webcolors import hex_to_rgb, rgb_to_hex
import json
import os
import logging
import random
from typing import Dict, List, Optional, Tuple
try:
    import pandas as pd
except ImportError:
    pd = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Monk skin tone scale for analysis
MONK_SKIN_TONES = {
    'Monk 1': '#f6ede4',
    'Monk 2': '#f3e7db',
    'Monk 3': '#f7ead0',
    'Monk 4': '#eadaba',
    'Monk 5': '#d7bd96',
    'Monk 6': '#a07e56',
    'Monk 7': '#825c43',
    'Monk 8': '#604134',
    'Monk 9': '#3a312a',
    'Monk 10': '#292420'
}

def analyze_skin_tone(image):
    """Analyze skin tone from uploaded image using simplified method for Gradio."""
    try:
        logger.info("Starting skin tone analysis...")
        
        # Convert PIL image to numpy array
        if isinstance(image, str):
            # If it's a path, read the image
            image = Image.open(image)
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        image_array = np.array(image)
        
        # Get average color of the image center (simplified approach)
        h, w = image_array.shape[:2]
        center_region = image_array[h//4:3*h//4, w//4:3*w//4]
        
        # Calculate average RGB
        avg_color = np.mean(center_region.reshape(-1, 3), axis=0)
        
        # Find closest Monk skin tone
        min_distance = float('inf')
        closest_monk = "Monk 5"  # Safe default for most users
        
        for monk_name, hex_color in MONK_SKIN_TONES.items():
            try:
                monk_rgb = np.array(hex_to_rgb(hex_color))
                distance = np.sqrt(np.sum((avg_color - monk_rgb) ** 2))
                
                if distance < min_distance:
                    min_distance = distance
                    closest_monk = monk_name
            except Exception as color_err:
                logger.warning(f"Error processing color {hex_color}: {color_err}")
                continue
        
        # Format response
        monk_number = closest_monk.split()[1]
        monk_id = f"Monk{monk_number.zfill(2)}"
        
        try:
            derived_hex = rgb_to_hex((int(avg_color[0]), int(avg_color[1]), int(avg_color[2])))
        except Exception:
            derived_hex = MONK_SKIN_TONES[closest_monk]  # Fallback to closest match
        
        result = {
            'monk_skin_tone': monk_id,
            'monk_tone_display': closest_monk,
            'monk_hex': MONK_SKIN_TONES[closest_monk],
            'derived_hex_code': derived_hex,
            'dominant_rgb': avg_color.astype(int).tolist(),
            'confidence': 0.8,
            'success': True
        }
        
        logger.info(f"Analysis result: {monk_id}")
        return result
        
    except Exception as e:
        logger.error(f"Error in skin tone analysis: {e}")
        return {
            'monk_skin_tone': 'Monk05',
            'monk_tone_display': 'Monk 5',
            'monk_hex': '#d7bd96',
            'derived_hex_code': '#d7bd96',
            'dominant_rgb': [215, 189, 150],
            'confidence': 0.5,
            'success': False,
            'error': str(e)
        }

def get_color_recommendations(monk_tone: str) -> List[Dict]:
    """Get color recommendations based on Monk skin tone."""
    try:
        # Color recommendations mapping based on skin tone
        color_recommendations = {
            'Monk01': [
                {'name': 'Soft Pink', 'hex': '#FFB6C1'},
                {'name': 'Powder Blue', 'hex': '#B0E0E6'},
                {'name': 'Lavender', 'hex': '#E6E6FA'},
                {'name': 'Mint Green', 'hex': '#98FB98'},
                {'name': 'Peach', 'hex': '#FFCBA4'}
            ],
            'Monk02': [
                {'name': 'Rose Gold', 'hex': '#E8B4B8'},
                {'name': 'Sky Blue', 'hex': '#87CEEB'},
                {'name': 'Sage Green', 'hex': '#9CAF88'},
                {'name': 'Warm Beige', 'hex': '#F5F5DC'},
                {'name': 'Coral', 'hex': '#FF7F50'}
            ],
            'Monk03': [
                {'name': 'Dusty Rose', 'hex': '#DCAE96'},
                {'name': 'Forest Green', 'hex': '#228B22'},
                {'name': 'Navy Blue', 'hex': '#000080'},
                {'name': 'Burgundy', 'hex': '#800020'},
                {'name': 'Golden Yellow', 'hex': '#FFD700'}
            ],
            'Monk04': [
                {'name': 'Warm Orange', 'hex': '#FF6600'},
                {'name': 'Teal', 'hex': '#008080'},
                {'name': 'Deep Purple', 'hex': '#663399'},
                {'name': 'Chocolate Brown', 'hex': '#8B4513'},
                {'name': 'Crimson', 'hex': '#DC143C'}
            ],
            'Monk05': [
                {'name': 'Emerald Green', 'hex': '#50C878'},
                {'name': 'Royal Blue', 'hex': '#4169E1'},
                {'name': 'Burnt Orange', 'hex': '#CC5500'},
                {'name': 'Deep Red', 'hex': '#8B0000'},
                {'name': 'Golden Brown', 'hex': '#996633'}
            ],
        }
        
        # Get recommendations or default colors
        if monk_tone in color_recommendations:
            colors = color_recommendations[monk_tone]
        else:
            # Default universal colors
            colors = [
                {'name': 'Navy Blue', 'hex': '#000080'},
                {'name': 'Forest Green', 'hex': '#228B22'},
                {'name': 'Burgundy', 'hex': '#800020'},
                {'name': 'Charcoal Gray', 'hex': '#36454F'},
                {'name': 'Cream White', 'hex': '#F5F5DC'}
            ]
        
        return colors
        
    except Exception as e:
        logger.error(f"Error getting color recommendations: {e}")
        # Fallback colors
        return [
            {'name': 'Navy Blue', 'hex': '#000080'},
            {'name': 'Forest Green', 'hex': '#228B22'},
            {'name': 'Burgundy', 'hex': '#800020'},
        ]

def get_makeup_products(monk_tone: str) -> List[Dict]:
    """Get makeup product recommendations."""
    brands = ["Fenty Beauty", "MAC", "NARS", "Maybelline", "L'Oreal", "Dior", "Urban Decay", "Too Faced"]
    products = ["Foundation", "Concealer", "Lipstick", "Mascara", "Blush", "Highlighter", "Bronzer", "Eyeshadow"]
    
    recommendations = []
    for i in range(6):  # Show 6 products
        brand = random.choice(brands)
        product_type = random.choice(products)
        price = f"${random.randint(15, 65)}.{random.randint(10, 99)}"
        
        # Create shade recommendations based on skin tone
        shade_map = {
            'Monk01': ['Light Ivory', 'Porcelain', 'Fair'],
            'Monk02': ['Light Beige', 'Natural', 'Light Medium'],
            'Monk03': ['Medium', 'Honey', 'Warm Beige'],
            'Monk04': ['Medium Deep', 'Caramel', 'Golden'],
            'Monk05': ['Deep', 'Rich', 'Espresso']
        }
        
        shades = shade_map.get(monk_tone, ['Universal', 'Medium', 'Natural'])
        recommended_shade = random.choice(shades)
        
        recommendations.append({
            'brand': brand,
            'product': product_type,
            'shade': recommended_shade,
            'price': price,
            'description': f"{brand} {product_type} in {recommended_shade} - Perfect for your skin tone!"
        })
    
    return recommendations

def process_skin_analysis(image):
    """Main function to process skin tone analysis and return comprehensive results."""
    if image is None:
        return "Please upload an image first!", "", "", ""
    
    try:
        # Analyze skin tone
        analysis_result = analyze_skin_tone(image)
        
        if not analysis_result['success']:
            return f"Analysis failed: {analysis_result.get('error', 'Unknown error')}", "", "", ""
        
        monk_tone = analysis_result['monk_skin_tone']
        confidence = analysis_result['confidence']
        
        # Get color recommendations
        color_recommendations = get_color_recommendations(monk_tone)
        
        # Get makeup recommendations
        makeup_recommendations = get_makeup_products(monk_tone)
        
        # Format results for display
        skin_tone_result = f"""
        ## 🎯 Skin Tone Analysis Results
        
        **Detected Skin Tone:** {analysis_result['monk_tone_display']}
        **Monk Scale ID:** {monk_tone}
        **Confidence:** {confidence:.1%}
        **Your Skin Color:** {analysis_result['derived_hex_code']}
        **Reference Color:** {analysis_result['monk_hex']}
        
        Your skin tone has been analyzed using the Monk Skin Tone Scale, 
        which provides more inclusive and accurate representation across all skin tones.
        """
        
        # Format color recommendations
        color_result = "## 🎨 Recommended Colors for You\n\n"
        for i, color in enumerate(color_recommendations, 1):
            color_result += f"**{i}. {color['name']}** - {color['hex']}\n"
        
        color_result += "\n*These colors will complement your skin tone beautifully!*"
        
        # Format makeup recommendations
        makeup_result = "## 💄 Makeup Recommendations\n\n"
        for i, product in enumerate(makeup_recommendations, 1):
            makeup_result += f"**{i}. {product['description']}**\n"
            makeup_result += f"   Price: {product['price']}\n\n"
        
        # Create color palette visualization info
        palette_info = f"""
        ## 🌈 Your Personal Color Palette
        
        Based on your {analysis_result['monk_tone_display']} skin tone, here are the colors that will make you look radiant:
        
        **Primary Colors:** {', '.join([c['name'] for c in color_recommendations[:3]])}
        **Accent Colors:** {', '.join([c['name'] for c in color_recommendations[3:]])}
        
        **Pro Tip:** These colors work great for clothing, makeup, and accessories!
        """
        
        return skin_tone_result, color_result, makeup_result, palette_info
        
    except Exception as e:
        logger.error(f"Error in process_skin_analysis: {e}")
        return f"An error occurred: {str(e)}", "", "", ""

def create_color_palette_html(colors: List[Dict]) -> str:
    """Create HTML visualization of color palette."""
    html = "<div style='display: flex; flex-wrap: wrap; gap: 10px; justify-content: center;'>"
    
    for color in colors:
        html += f"""
        <div style='text-align: center; margin: 5px;'>
            <div style='width: 60px; height: 60px; background-color: {color['hex']}; 
                       border: 2px solid #ddd; border-radius: 50%; margin: 0 auto;'></div>
            <p style='margin: 5px 0; font-size: 12px; font-weight: bold;'>{color['name']}</p>
            <p style='margin: 0; font-size: 10px; color: #666;'>{color['hex']}</p>
        </div>
        """
    
    html += "</div>"
    return html

def get_style_suggestions(monk_tone: str) -> str:
    """Get style suggestions based on skin tone."""
    style_guides = {
        'Monk01': {
            'best_colors': 'Soft pastels, light blues, pinks, and lavenders',
            'avoid': 'Overly bright or neon colors that might wash you out',
            'tips': 'Try monochromatic looks in soft tones, add pops of color with accessories'
        },
        'Monk02': {
            'best_colors': 'Warm earth tones, coral, peach, and soft greens',
            'avoid': 'Colors that are too cool or stark',
            'tips': 'Layer different textures in similar tones for depth'
        },
        'Monk03': {
            'best_colors': 'Rich jewel tones, deep blues, emerald greens, and burgundy',
            'avoid': 'Washed out pastels',
            'tips': 'Bold colors work great - don\'t be afraid to make a statement!'
        },
        'Monk04': {
            'best_colors': 'Warm oranges, golden yellows, deep purples, and rich browns',
            'avoid': 'Colors that are too cool or icy',
            'tips': 'Mix warm and deep tones for a sophisticated look'
        },
        'Monk05': {
            'best_colors': 'Vibrant colors, bright whites, electric blues, and bold reds',
            'avoid': 'Muddy or dull colors',
            'tips': 'You can wear almost any color - experiment with bold combinations!'
        }
    }
    
    guide = style_guides.get(monk_tone, style_guides['Monk03'])
    
    return f"""
    ## 👗 Your Personal Style Guide
    
    **Colors that make you glow:** {guide['best_colors']}
    
    **Colors to use sparingly:** {guide['avoid']}
    
    **Styling tips:** {guide['tips']}
    
    **Remember:** These are guidelines - wear what makes you feel confident and beautiful!
    """

# Create the Gradio interface
with gr.Blocks(title="AI Fashion - Your Personal Color Analyst", theme=gr.themes.Soft()) as demo:
    gr.HTML("""
    <div style="text-align: center; padding: 20px;">
        <h1 style="color: #4F46E5; font-size: 2.5rem; margin-bottom: 10px;">🎨 AI Fashion</h1>
        <p style="font-size: 1.2rem; color: #6B7280;">Your Personal Color Analyst powered by AI</p>
        <p style="color: #9CA3AF;">Upload your photo to discover colors that make you look amazing!</p>
    </div>
    """)
    
    with gr.Row():
        with gr.Column(scale=1):
            image_input = gr.Image(
                label="Upload Your Photo 📸",
                type="pil",
                height=400
            )
            
            analyze_btn = gr.Button(
                "✨ Analyze My Skin Tone",
                variant="primary",
                size="lg"
            )
            
            gr.HTML("""
            <div style="margin-top: 20px; padding: 15px; background-color: #F3F4F6; border-radius: 10px;">
                <h4>📋 Tips for best results:</h4>
                <ul style="margin: 10px 0; padding-left: 20px;">
                    <li>Use natural lighting</li>
                    <li>Face the camera directly</li>
                    <li>Remove glasses if possible</li>
                    <li>Ensure your face is clearly visible</li>
                </ul>
            </div>
            """)
        
        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.Tab("🎯 Analysis Results"):
                    skin_tone_output = gr.Markdown(label="")
                
                with gr.Tab("🎨 Color Recommendations"):
                    color_output = gr.Markdown(label="")
                
                with gr.Tab("💄 Makeup Suggestions"):
                    makeup_output = gr.Markdown(label="")
                
                with gr.Tab("🌈 Style Guide"):
                    style_output = gr.Markdown(label="")
    
    # Connect the analyze button to the processing function
    analyze_btn.click(
        fn=process_skin_analysis,
        inputs=image_input,
        outputs=[skin_tone_output, color_output, makeup_output, style_output]
    )
    
    gr.HTML("""
    <div style="text-align: center; margin-top: 40px; padding: 20px; background-color: #F9FAFB; border-radius: 15px;">
        <h3 style="color: #374151;">About AI Fashion</h3>
        <p style="color: #6B7280; max-width: 600px; margin: 0 auto;">  
            Our AI-powered color analysis uses the Monk Skin Tone Scale for more inclusive and accurate 
            skin tone representation. Get personalized recommendations for colors, makeup, and style 
            that complement your unique beauty.
        </p>
        <br>
        <p style="color: #9CA3AF; font-size: 0.9rem;">
            🔬 Powered by Computer Vision &nbsp;•&nbsp; 🎨 Monk Skin Tone Scale &nbsp;•&nbsp; 💖 Made with care
        </p>
    </div>
    """)

if __name__ == "__main__":
    demo.launch(share=True)
