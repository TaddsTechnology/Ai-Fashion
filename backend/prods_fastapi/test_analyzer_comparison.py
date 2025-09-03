#!/usr/bin/env python3
"""
Test script to compare the original and improved skin tone analyzers.
This script will test both analyzers on sample images and compare their results.
"""

import sys
import os
import numpy as np
import cv2
from PIL import Image
import logging
import time
import json
from typing import Dict, List

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from enhanced_skin_tone_analyzer import EnhancedSkinToneAnalyzer
    from improved_skin_tone_analyzer import ImprovedSkinToneAnalyzer
    ANALYZERS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import analyzers: {e}")
    ANALYZERS_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Sample Monk skin tone mappings for testing
SAMPLE_MONK_TONES = {
    'Monk 1': '#f6ede4',   # Very Light
    'Monk 2': '#f3e7db',   # Light  
    'Monk 3': '#f7ead0',   # Light Medium
    'Monk 4': '#eadaba',   # Medium Light
    'Monk 5': '#d7bd96',   # Medium
    'Monk 6': '#a07e56',   # Medium Dark
    'Monk 7': '#825c43',   # Dark
    'Monk 8': '#604134',   # Dark
    'Monk 9': '#3a312a',   # Very Dark
    'Monk 10': '#292420'   # Very Dark
}

def create_synthetic_face_image(skin_color_rgb: tuple, size: tuple = (300, 300)) -> np.ndarray:
    """Create a synthetic face image for testing purposes."""
    # Create base face shape
    img = np.full((*size, 3), skin_color_rgb, dtype=np.uint8)
    
    # Add some facial features for more realistic testing
    h, w = size
    
    # Add slight color variations to simulate real skin
    noise = np.random.normal(0, 5, (*size, 3))
    img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    
    # Create an oval face shape
    center = (w // 2, h // 2)
    axes = (w // 3, h // 2)
    
    # Create face mask
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.ellipse(mask, center, axes, 0, 0, 360, 255, -1)
    
    # Apply mask to create face shape
    face_img = np.zeros_like(img)
    for c in range(3):
        face_img[:, :, c] = cv2.bitwise_and(img[:, :, c], mask)
    
    # Add background
    bg_color = (50, 100, 150)  # Blue background
    bg_mask = cv2.bitwise_not(mask)
    for c in range(3):
        face_img[:, :, c] = cv2.bitwise_or(face_img[:, :, c], 
                                          cv2.bitwise_and(np.full((h, w), bg_color[c], dtype=np.uint8), bg_mask))
    
    return face_img

def run_analyzer_comparison(test_images: List[np.ndarray], image_names: List[str]) -> Dict:
    """Run comparison between original and improved analyzers."""
    if not ANALYZERS_AVAILABLE:
        logger.error("Analyzers not available for testing")
        return {}
    
    # Initialize analyzers
    try:
        original_analyzer = EnhancedSkinToneAnalyzer()
        improved_analyzer = ImprovedSkinToneAnalyzer()
        logger.info("Both analyzers initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize analyzers: {e}")
        return {}
    
    results = {
        'original': [],
        'improved': [],
        'comparison': []
    }
    
    for i, (image, name) in enumerate(zip(test_images, image_names)):
        logger.info(f"\nTesting image {i+1}: {name}")
        
        # Test original analyzer
        start_time = time.time()
        try:
            original_result = original_analyzer.analyze_skin_tone(image, SAMPLE_MONK_TONES)
            original_time = time.time() - start_time
            original_result['processing_time'] = round(original_time, 3)
            logger.info(f"Original analyzer: {original_result.get('monk_tone_display', 'Unknown')} "
                       f"(confidence: {original_result.get('confidence', 0):.2f}, "
                       f"time: {original_time:.3f}s)")
        except Exception as e:
            logger.error(f"Original analyzer failed: {e}")
            original_result = {'error': str(e), 'success': False, 'processing_time': 0}
        
        # Test improved analyzer
        start_time = time.time()
        try:
            improved_result = improved_analyzer.analyze_skin_tone_enhanced(image, SAMPLE_MONK_TONES)
            improved_time = time.time() - start_time
            improved_result['processing_time'] = round(improved_time, 3)
            logger.info(f"Improved analyzer: {improved_result.get('monk_tone_display', 'Unknown')} "
                       f"(confidence: {improved_result.get('confidence', 0):.2f}, "
                       f"time: {improved_time:.3f}s)")
        except Exception as e:
            logger.error(f"Improved analyzer failed: {e}")
            improved_result = {'error': str(e), 'success': False, 'processing_time': 0}
        
        # Compare results
        comparison = compare_results(original_result, improved_result, name)
        
        results['original'].append(original_result)
        results['improved'].append(improved_result)
        results['comparison'].append(comparison)
    
    return results

def compare_results(original: Dict, improved: Dict, image_name: str) -> Dict:
    """Compare results from both analyzers."""
    comparison = {
        'image_name': image_name,
        'both_successful': original.get('success', False) and improved.get('success', False),
        'original_successful': original.get('success', False),
        'improved_successful': improved.get('success', False),
        'same_monk_tone': False,
        'confidence_difference': 0,
        'time_difference': 0,
        'improvements': []
    }
    
    if comparison['both_successful']:
        # Compare Monk tones
        orig_monk = original.get('monk_skin_tone', '')
        imp_monk = improved.get('monk_skin_tone', '')
        comparison['same_monk_tone'] = orig_monk == imp_monk
        
        # Compare confidences
        orig_conf = original.get('confidence', 0)
        imp_conf = improved.get('confidence', 0)
        comparison['confidence_difference'] = round(imp_conf - orig_conf, 3)
        
        # Compare processing times
        orig_time = original.get('processing_time', 0)
        imp_time = improved.get('processing_time', 0)
        comparison['time_difference'] = round(imp_time - orig_time, 3)
        
        # Identify improvements
        if imp_conf > orig_conf + 0.05:  # Significant confidence improvement
            comparison['improvements'].append('Higher confidence')
        
        if improved.get('landmarks_detected', False):
            comparison['improvements'].append('Landmark detection')
        
        if improved.get('clustering_confidence', 0) > 0.7:
            comparison['improvements'].append('Good clustering')
        
        if improved.get('regions_analyzed', 0) > original.get('regions_analyzed', 0):
            comparison['improvements'].append('More regions analyzed')
    
    elif comparison['improved_successful'] and not comparison['original_successful']:
        comparison['improvements'].append('Only improved analyzer succeeded')
    
    return comparison

def generate_test_report(results: Dict) -> str:
    """Generate a comprehensive test report."""
    if not results:
        return "No results available for reporting."
    
    report = []
    report.append("=" * 60)
    report.append("SKIN TONE ANALYZER COMPARISON REPORT")
    report.append("=" * 60)
    
    # Summary statistics
    total_tests = len(results['comparison'])
    both_success = sum(1 for c in results['comparison'] if c['both_successful'])
    orig_only_success = sum(1 for c in results['comparison'] 
                           if c['original_successful'] and not c['improved_successful'])
    imp_only_success = sum(1 for c in results['comparison'] 
                          if c['improved_successful'] and not c['original_successful'])
    
    report.append(f"\nSUMMARY:")
    report.append(f"Total test images: {total_tests}")
    report.append(f"Both analyzers successful: {both_success}/{total_tests}")
    report.append(f"Only original successful: {orig_only_success}/{total_tests}")
    report.append(f"Only improved successful: {imp_only_success}/{total_tests}")
    
    # Detailed comparison
    if both_success > 0:
        same_monk_count = sum(1 for c in results['comparison'] if c.get('same_monk_tone', False))
        avg_conf_diff = np.mean([c.get('confidence_difference', 0) for c in results['comparison'] 
                                if c['both_successful']])
        avg_time_diff = np.mean([c.get('time_difference', 0) for c in results['comparison'] 
                                if c['both_successful']])
        
        report.append(f"\nDETAILED ANALYSIS:")
        report.append(f"Same Monk tone detected: {same_monk_count}/{both_success}")
        report.append(f"Average confidence difference: {avg_conf_diff:.3f}")
        report.append(f"Average time difference: {avg_time_diff:.3f}s")
    
    # Individual test results
    report.append(f"\nINDIVIDUAL TEST RESULTS:")
    report.append("-" * 60)
    
    for i, (orig, imp, comp) in enumerate(zip(results['original'], 
                                             results['improved'], 
                                             results['comparison'])):
        report.append(f"\nTest {i+1}: {comp['image_name']}")
        
        if comp['both_successful']:
            report.append(f"  Original: {orig.get('monk_tone_display', 'N/A')} "
                         f"(conf: {orig.get('confidence', 0):.2f}, "
                         f"time: {orig.get('processing_time', 0):.3f}s)")
            report.append(f"  Improved: {imp.get('monk_tone_display', 'N/A')} "
                         f"(conf: {imp.get('confidence', 0):.2f}, "
                         f"time: {imp.get('processing_time', 0):.3f}s)")
            
            if comp['improvements']:
                report.append(f"  Improvements: {', '.join(comp['improvements'])}")
        else:
            if not comp['original_successful']:
                report.append(f"  Original: FAILED - {orig.get('error', 'Unknown error')}")
            if not comp['improved_successful']:
                report.append(f"  Improved: FAILED - {imp.get('error', 'Unknown error')}")
    
    return "\n".join(report)

def main():
    """Main function to run the comparison test."""
    logger.info("Starting skin tone analyzer comparison test")
    
    if not ANALYZERS_AVAILABLE:
        logger.error("Cannot run tests - analyzers not available")
        return
    
    # Create test images with different skin tones
    test_images = []
    image_names = []
    
    # Test with synthetic images of different skin tones
    skin_colors = [
        ((250, 240, 230), "Very Light Skin (Synthetic)"),
        ((220, 200, 180), "Light Skin (Synthetic)"),
        ((200, 170, 140), "Medium Light Skin (Synthetic)"),
        ((180, 140, 110), "Medium Skin (Synthetic)"),
        ((140, 100, 80), "Medium Dark Skin (Synthetic)"),
        ((100, 70, 50), "Dark Skin (Synthetic)"),
        ((60, 40, 30), "Very Dark Skin (Synthetic)")
    ]
    
    logger.info(f"Creating {len(skin_colors)} synthetic test images...")
    for color, name in skin_colors:
        synthetic_image = create_synthetic_face_image(color)
        test_images.append(synthetic_image)
        image_names.append(name)
    
    # Run comparison
    logger.info("Running analyzer comparison...")
    results = run_analyzer_comparison(test_images, image_names)
    
    if results:
        # Generate and display report
        report = generate_test_report(results)
        print("\n" + report)
        
        # Save results to file
        output_file = "analyzer_comparison_results.json"
        try:
            # Convert numpy arrays to lists for JSON serialization
            json_results = {}
            for key, value in results.items():
                if isinstance(value, list):
                    json_results[key] = []
                    for item in value:
                        json_item = {}
                        for k, v in item.items():
                            if isinstance(v, np.ndarray):
                                json_item[k] = v.tolist()
                            else:
                                json_item[k] = v
                        json_results[key].append(json_item)
                else:
                    json_results[key] = value
            
            with open(output_file, 'w') as f:
                json.dump(json_results, f, indent=2)
            logger.info(f"Results saved to {output_file}")
            
        except Exception as e:
            logger.warning(f"Failed to save results: {e}")
    
    logger.info("Comparison test completed")

if __name__ == "__main__":
    main()
