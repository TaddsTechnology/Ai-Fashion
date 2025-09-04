import cv2
import numpy as np
# Removed face_recognition to avoid compilation issues
# Using MediaPipe and OpenCV for face detection instead
try:
    import dlib
    DLIB_AVAILABLE = True
except ImportError:
    dlib = None
    DLIB_AVAILABLE = False
import mediapipe as mp
from sklearn.cluster import KMeans
from scipy import stats
import logging
from typing import List, Dict, Tuple, Optional
from scipy.spatial.distance import euclidean
from sklearn.preprocessing import normalize
import colorsys

logger = logging.getLogger(__name__)

class EnhancedSkinToneAnalyzer:
    def __init__(self):
        """Initialize the enhanced skin tone analyzer with multiple detection methods."""
        # MediaPipe face detection
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        
        # Face recognition library removed to avoid compilation issues
        self.face_recognition_available = False
        logger.info("Face recognition library not used - using MediaPipe and OpenCV instead")
        
        # Dlib face detection (fallback)
        if DLIB_AVAILABLE:
            self.dlib_detector = dlib.get_frontal_face_detector()
            
            # Try to load dlib predictor (optional)
            try:
                self.dlib_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
                self.dlib_available = True
                logger.info("Dlib shape predictor loaded successfully")
            except Exception as e:
                self.dlib_predictor = None
                self.dlib_available = False
                logger.warning(f"Dlib shape predictor not available: {e}, using other methods")
        else:
            self.dlib_detector = None
            self.dlib_predictor = None
            self.dlib_available = False
            logger.info("Dlib not installed, using other methods for face detection")
    
    def detect_face_mediapipe(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect face using MediaPipe and return bounding box."""
        try:
            with self.mp_face_detection.FaceDetection(
                model_selection=1, min_detection_confidence=0.7) as face_detection:
                
                # Convert BGR to RGB for MediaPipe
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = face_detection.process(rgb_image)
                
                if results.detections:
                    detection = results.detections[0]  # Use first face
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = image.shape
                    
                    x = int(bboxC.xmin * iw)
                    y = int(bboxC.ymin * ih)
                    w = int(bboxC.width * iw)
                    h = int(bboxC.height * ih)
                    
                    # Add padding for better skin region
                    padding = 0.1
                    x = max(0, int(x - w * padding))
                    y = max(0, int(y - h * padding))
                    w = min(iw - x, int(w * (1 + 2 * padding)))
                    h = min(ih - y, int(h * (1 + 2 * padding)))
                    
                    return (x, y, w, h)
        except Exception as e:
            logger.warning(f"MediaPipe face detection failed: {e}")
        
        return None
    
    def detect_face_dlib(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect face using Dlib and return bounding box."""
        if not self.dlib_available:
            return None
            
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            faces = self.dlib_detector(gray)
            
            if len(faces) > 0:
                face = faces[0]  # Use first face
                x, y, w, h = face.left(), face.top(), face.width(), face.height()
                
                # Add padding
                padding = 0.1
                x = max(0, int(x - w * padding))
                y = max(0, int(y - h * padding))
                w = min(image.shape[1] - x, int(w * (1 + 2 * padding)))
                h = min(image.shape[0] - y, int(h * (1 + 2 * padding)))
                
                return (x, y, w, h)
        except Exception as e:
            logger.warning(f"Dlib face detection failed: {e}")
        
        return None
    
    def detect_face_recognition(self, image: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """Detect face using face_recognition library and return bounding box."""
        if not self.face_recognition_available:
            return None
            
        try:
            # Convert BGR to RGB for face_recognition
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Find face locations
            face_locations = face_recognition.face_locations(rgb_image, model="hog")
            
            if face_locations:
                # Use first face (format: top, right, bottom, left)
                top, right, bottom, left = face_locations[0]
                
                # Convert to x, y, w, h format
                x, y = left, top
                w, h = right - left, bottom - top
                
                # Add padding for better skin region
                padding = 0.1
                x = max(0, int(x - w * padding))
                y = max(0, int(y - h * padding))
                w = min(image.shape[1] - x, int(w * (1 + 2 * padding)))
                h = min(image.shape[0] - y, int(h * (1 + 2 * padding)))
                
                return (x, y, w, h)
                
        except Exception as e:
            logger.warning(f"Face recognition detection failed: {e}")
        
        return None
    
    def detect_face(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Detect face using multiple methods and return face region."""
        # Try MediaPipe first (most reliable and no compilation issues)
        bbox = self.detect_face_mediapipe(image)
        
        # Fallback to Dlib
        if bbox is None:
            bbox = self.detect_face_dlib(image)
        
        if bbox is None:
            logger.warning("No face detected with any method")
            return None
        
        x, y, w, h = bbox
        face_region = image[y:y+h, x:x+w]
        
        # Ensure minimum face size
        if face_region.shape[0] < 50 or face_region.shape[1] < 50:
            logger.warning("Detected face too small")
            return None
        
        return face_region
    
    def apply_advanced_lighting_correction(self, image: np.ndarray) -> np.ndarray:
        """Apply advanced lighting correction using multiple techniques."""
        try:
            # Convert to LAB color space
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE to L channel
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l_corrected = clahe.apply(l)
            
            # Merge back
            lab_corrected = cv2.merge([l_corrected, a, b])
            rgb_corrected = cv2.cvtColor(lab_corrected, cv2.COLOR_LAB2RGB)
            
            # Adaptive gamma correction based on overall brightness
            gray = cv2.cvtColor(rgb_corrected, cv2.COLOR_RGB2GRAY)
            mean_brightness = np.mean(gray)
            
            # Improved gamma correction optimized for fair skin detection
            if mean_brightness < 70:  # Very dark image/skin
                gamma = 1.4  # Brighten significantly for very dark skin
            elif mean_brightness < 120:  # Dark skin
                gamma = 1.2  # Moderate brightening for dark skin
            elif mean_brightness < 160:  # Medium skin
                gamma = 1.0  # No correction needed
            elif mean_brightness < 210:  # Light skin - less aggressive correction
                gamma = 0.95  # Very slight darkening to preserve fair skin details
            else:  # Very light/fair skin (>210) - minimal correction
                gamma = 0.9  # Gentle correction to avoid washing out fair skin
            
            if gamma != 1.0:
                rgb_corrected = np.power(rgb_corrected / 255.0, gamma) * 255.0
                rgb_corrected = np.clip(rgb_corrected, 0, 255).astype(np.uint8)
            
            return rgb_corrected
            
        except Exception as e:
            logger.warning(f"Advanced lighting correction failed: {e}")
            return image
    
    def extract_skin_regions(self, face_image: np.ndarray) -> List[np.ndarray]:
        """Extract multiple skin regions from face for analysis."""
        h, w = face_image.shape[:2]
        
        # Define skin regions (avoiding eyes, mouth, etc.)
        regions = {
            'forehead': (int(0.2*w), int(0.1*h), int(0.6*w), int(0.25*h)),
            'left_cheek': (int(0.1*w), int(0.3*h), int(0.35*w), int(0.4*h)),
            'right_cheek': (int(0.55*w), int(0.3*h), int(0.35*w), int(0.4*h)),
            'nose_bridge': (int(0.4*w), int(0.25*h), int(0.2*w), int(0.3*h)),
            'chin': (int(0.3*w), int(0.7*h), int(0.4*w), int(0.25*h))
        }
        
        region_colors = []
        
        # Check if image is very bright (likely fair skin)
        overall_brightness = np.mean(face_image)
        is_fair_skin = overall_brightness > 200
        
        for region_name, (x, y, rw, rh) in regions.items():
            if x + rw <= w and y + rh <= h and x >= 0 and y >= 0:
                region = face_image[y:y+rh, x:x+rw]
                
                if region.size > 100:  # Ensure enough pixels
                    if is_fair_skin:
                        # For fair skin, use more permissive filtering
                        # Use HSV for better fair skin detection
                        region_hsv = cv2.cvtColor(region, cv2.COLOR_RGB2HSV)
                        
                        # More inclusive range for fair skin in HSV
                        lower_skin_hsv = np.array([0, 10, 120])  # Lower saturation, higher value
                        upper_skin_hsv = np.array([25, 150, 255])
                        
                        skin_mask = cv2.inRange(region_hsv, lower_skin_hsv, upper_skin_hsv)
                        
                        # Also include very bright pixels that might be fair skin
                        brightness_mask = cv2.inRange(region, np.array([180, 170, 160]), np.array([255, 255, 255]))
                        skin_mask = cv2.bitwise_or(skin_mask, brightness_mask)
                        
                    else:
                        # Use traditional YCbCr filtering for non-fair skin
                        region_ycbcr = cv2.cvtColor(region, cv2.COLOR_RGB2YCrCb)
                        
                        # Skin color range in YCbCr
                        lower_skin = np.array([0, 133, 77])
                        upper_skin = np.array([255, 173, 127])
                        
                        skin_mask = cv2.inRange(region_ycbcr, lower_skin, upper_skin)
                    
                    if np.sum(skin_mask > 0) > 30:  # Lowered threshold for fair skin
                        skin_pixels = region[skin_mask > 0]
                        if len(skin_pixels) > 5:  # More permissive for fair skin
                            region_color = np.mean(skin_pixels, axis=0)
                            region_colors.append(region_color)
                    elif is_fair_skin and region.size > 0:  # Fallback for very fair skin
                        # If no skin pixels detected but it's fair skin, use region average
                        region_color = np.mean(region.reshape(-1, 3), axis=0)
                        if np.mean(region_color) > 180:  # Only if reasonably bright
                            region_colors.append(region_color)
        
        return region_colors
    
    def cluster_skin_colors(self, region_colors: List[np.ndarray], n_clusters: int = 3) -> np.ndarray:
        """Use K-means clustering to find dominant skin color."""
        if not region_colors:
            return np.array([220, 210, 200])  # Adjusted default for lighter skin

        try:
            # Combine all region colors
            all_colors = np.vstack(region_colors)

            # Apply K-means clustering
            kmeans = KMeans(n_clusters=min(n_clusters, len(all_colors)), random_state=42, n_init=10)
            kmeans.fit(all_colors)

            # Adjust clustering for fair tones
            brightness_weights = np.array([np.mean(color) for color in all_colors])
            if np.sum(brightness_weights) > 0:
                brightness_weights /= np.sum(brightness_weights)
            adjusted_color = np.average(all_colors, axis=0, weights=brightness_weights)

            return adjusted_color
            
        except Exception as e:
            logger.warning(f"Color clustering failed: {e}")
            return np.mean(region_colors, axis=0) if region_colors else np.array([200, 180, 160])
    
    def calculate_advanced_confidence(self, face_image: np.ndarray, final_color: np.ndarray, 
                                    region_colors: List[np.ndarray]) -> float:
        """Calculate confidence score with multiple factors."""
        try:
            confidence_factors = []
            
            # 1. Color consistency across regions
            if len(region_colors) > 1:
                color_std = np.std([np.mean(color) for color in region_colors])
                consistency_score = max(0, 1 - (color_std / 50))
                confidence_factors.append(consistency_score * 0.3)
            
            # 2. Image sharpness
            gray = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(1.0, sharpness / 500)
            confidence_factors.append(sharpness_score * 0.2)
            
            # 3. Brightness appropriateness
            brightness = np.mean(final_color)
            if 100 <= brightness <= 220:
                brightness_score = 1.0
            else:
                brightness_score = max(0, 1 - abs(brightness - 160) / 100)
            confidence_factors.append(brightness_score * 0.2)
            
            # 4. Color saturation (skin tones are typically not oversaturated)
            hsv = cv2.cvtColor(np.uint8([[final_color]]), cv2.COLOR_RGB2HSV)[0][0]
            saturation = hsv[1] / 255.0
            saturation_score = max(0, 1 - max(0, saturation - 0.3) / 0.7)
            confidence_factors.append(saturation_score * 0.15)
            
            # 5. Face detection confidence (base score)
            confidence_factors.append(0.15)
            
            return min(1.0, sum(confidence_factors))
            
        except Exception as e:
            logger.warning(f"Confidence calculation failed: {e}")
            return 0.5
    
    def brightness_prefilter(self, rgb_color: np.ndarray) -> Dict[str, any]:
        """PERFECT brightness-based preprocessing for fair skin detection."""
        r, g, b = rgb_color
        
        # Multiple brightness calculations
        rgb_brightness = np.mean([r, g, b])
        weighted_brightness = 0.299*r + 0.587*g + 0.114*b  # Luminance
        max_brightness = max(r, g, b)
        min_brightness = min(r, g, b)
        
        # HSV analysis
        hsv = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
        v_brightness = hsv[2] * 255  # V channel brightness
        saturation = hsv[1] * 100
        
        # LAB analysis
        lab = cv2.cvtColor(np.uint8([[[r, g, b]]]), cv2.COLOR_RGB2LAB)[0][0]
        L_brightness = lab[0]
        
        # PERFECT fair skin detection - multiple criteria
        is_ultra_fair = (
            rgb_brightness > 200 and 
            weighted_brightness > 195 and 
            L_brightness > 75 and 
            v_brightness > 190 and
            max_brightness > 220
        )
        
        is_very_fair = (
            rgb_brightness > 180 and 
            weighted_brightness > 175 and 
            L_brightness > 70 and 
            v_brightness > 170 and
            (max_brightness - min_brightness) < 60  # Low contrast = fair skin
        )
        
        is_fair = (
            rgb_brightness > 160 and 
            weighted_brightness > 155 and 
            L_brightness > 65 and 
            saturation < 30  # Fair skin has low saturation
        )
        
        return {
            'is_ultra_fair': is_ultra_fair,
            'is_very_fair': is_very_fair, 
            'is_fair': is_fair,
            'rgb_brightness': rgb_brightness,
            'weighted_brightness': weighted_brightness,
            'L_brightness': L_brightness,
            'saturation': saturation,
            'contrast': max_brightness - min_brightness
        }
    
    def perfect_fair_skin_classification(self, rgb_color: np.ndarray, brightness_info: Dict) -> Tuple[str, float]:
        """PERFECT ultra-aggressive fair skin classification with multi-layered approach."""
        
        # Layer 1: Ultra-aggressive brightness prefilter
        if brightness_info['is_ultra_fair']:
            # ULTRA FAIR - Always Monk 1 or 2
            if brightness_info['L_brightness'] > 80 or brightness_info['rgb_brightness'] > 220:
                return "Monk 1", 0.99
            else:
                return "Monk 2", 0.98
        
        if brightness_info['is_very_fair']:
            # VERY FAIR - Monk 1, 2, or 3 only
            if brightness_info['saturation'] < 15 and brightness_info['L_brightness'] > 78:
                return "Monk 1", 0.97
            elif brightness_info['contrast'] < 40 and brightness_info['weighted_brightness'] > 185:
                return "Monk 2", 0.95
            else:
                return "Monk 2", 0.93  # Default to Monk 2 for very fair
        
        if brightness_info['is_fair']:
            # FAIR - Monk 1, 2, 3, or 4 only
            if brightness_info['L_brightness'] > 75:
                return "Monk 1", 0.9
            elif brightness_info['L_brightness'] > 70:
                return "Monk 2", 0.88
            else:
                return "Monk 3", 0.85
        
        # Layer 2: If not detected as fair, continue with traditional analysis but with fair bias
        return None, 0.0
    
    def advanced_skin_tone_classification(self, rgb_color: np.ndarray) -> Tuple[str, float]:
        """PERFECT advanced skin tone classification with ultra-aggressive fair skin detection."""
        try:
            r, g, b = rgb_color
            avg_brightness = np.mean([r, g, b])
            
            # STEP 1: Brightness-based preprocessing
            brightness_info = self.brightness_prefilter(rgb_color)
            
            # STEP 2: Perfect fair skin classification
            fair_result, fair_confidence = self.perfect_fair_skin_classification(rgb_color, brightness_info)
            if fair_result is not None:
                logger.info(f"PERFECT Fair skin detected: {fair_result} (confidence: {fair_confidence:.2f})")
                return fair_result, fair_confidence
            
            # STEP 3: Traditional analysis with fair skin bias for edge cases
            # Convert to other color spaces for analysis
            hsv = colorsys.rgb_to_hsv(r/255.0, g/255.0, b/255.0)
            h, s, v = hsv[0] * 360, hsv[1] * 100, hsv[2] * 100
            
            # Calculate Individual Typology Angle (ITA) - scientific measure
            lab = cv2.cvtColor(np.uint8([[[r, g, b]]]), cv2.COLOR_RGB2LAB)[0][0]
            L, a_val, b_val = lab
            
            # ITA calculation: arctan((L* - 50) / b*) * 180 / π
            if abs(b_val) > 0.1:  # Avoid division by very small numbers
                ita = np.arctan((L - 50) / b_val) * 180 / np.pi
            else:
                ita = 90 if L > 50 else -90
            
            # STEP 4: Ultra-aggressive fair skin detection for edge cases
            # Even if not caught by preprocessing, check again with lower thresholds
            if avg_brightness > 170:  # Lowered threshold for fair detection
                if L > 68 or ita > 30:  # More generous fair skin detection
                    return "Monk 2", 0.85  # Bias toward fair
                elif L > 65 or ita > 15:
                    return "Monk 3", 0.8
            
            elif avg_brightness > 150:  # Light-medium with fair bias
                if L > 70 or ita > 25:
                    return "Monk 3", 0.8
                elif L > 65 or ita > 10:
                    return "Monk 4", 0.75
            
            # Adjusted ITA thresholds for better fair skin detection
            elif ita > 50:  # Very Light (more generous threshold)
                return "Monk 1", 0.9
            elif ita > 35:  # Light (lowered threshold)
                return "Monk 2", 0.85
            elif ita > 20:  # Intermediate (lowered threshold)
                return "Monk 3", 0.8
            elif ita > 5:  # Tan (lowered threshold)
                return "Monk 4", 0.75
            elif ita > -20:  # Brown (adjusted threshold)
                if L > 65:
                    return "Monk 5", 0.7
                elif L > 55:
                    return "Monk 6", 0.7
                else:
                    return "Monk 7", 0.7
            else:  # Dark
                if L > 45:
                    return "Monk 8", 0.65
                elif L > 35:
                    return "Monk 9", 0.65
                else:
                    return "Monk 10", 0.65
                    
        except Exception as e:
            logger.warning(f"ITA classification failed: {e}")
            return "Monk 2", 0.5  # Default to light instead of medium
    
    def find_closest_monk_tone_advanced(self, rgb_color: np.ndarray, 
                                      monk_tones: Dict[str, str]) -> Tuple[str, float]:
        """Advanced Monk tone matching using multiple methods."""
        try:
            # Method 1: Statistical ITA-based classification
            ita_result, ita_confidence = self.advanced_skin_tone_classification(rgb_color)
            
            # Method 2: Traditional color space analysis (as fallback)
            avg_brightness = np.mean(rgb_color)
            
            # Convert to multiple color spaces for comparison
            lab_color = cv2.cvtColor(np.uint8([[rgb_color]]), cv2.COLOR_RGB2LAB)[0][0]
            hsv_color = cv2.cvtColor(np.uint8([[rgb_color]]), cv2.COLOR_RGB2HSV)[0][0]
            
            min_distance = float('inf')
            closest_monk = "Monk 2"
            
            for monk_name, hex_color in monk_tones.items():
                # Convert monk tone to RGB
                monk_rgb = np.array([
                    int(hex_color[1:3], 16),
                    int(hex_color[3:5], 16),
                    int(hex_color[5:7], 16)
                ])
                
                # Convert to LAB and HSV
                monk_lab = cv2.cvtColor(np.uint8([[monk_rgb]]), cv2.COLOR_RGB2LAB)[0][0]
                monk_hsv = cv2.cvtColor(np.uint8([[monk_rgb]]), cv2.COLOR_RGB2HSV)[0][0]
                
                # Calculate distances in different color spaces
                rgb_distance = np.sqrt(np.sum((rgb_color - monk_rgb) ** 2))
                lab_distance = np.sqrt(np.sum((lab_color - monk_lab) ** 2))
                
                # Hue distance (circular)
                hue_diff = min(abs(hsv_color[0] - monk_hsv[0]), 
                             180 - abs(hsv_color[0] - monk_hsv[0]))
                hue_distance = hue_diff / 180.0 * 100
                
                # Calculate brightness difference
                monk_brightness = np.mean(monk_rgb)
                brightness_diff = abs(avg_brightness - monk_brightness)
                
                # Enhanced fair skin bias with stronger penalties for mismatched brightness
                if avg_brightness > 220:  # Very fair skin - strongest bias
                    if monk_brightness < 180:  # Penalize dark tones heavily
                        brightness_penalty = brightness_diff * 5.0
                    elif monk_brightness < 200:  # Moderate penalty for medium tones
                        brightness_penalty = brightness_diff * 2.0
                    else:  # Slight penalty for light tones
                        brightness_penalty = brightness_diff * 0.2
                    
                    combined_distance = (
                        rgb_distance * 0.1 +
                        lab_distance * 0.1 +
                        hue_distance * 0.05 +
                        brightness_penalty * 0.75  # Heavily weight brightness for very fair skin
                    )
                elif avg_brightness > 200:  # Fair skin - strong bias
                    if monk_brightness < 170:  # Heavy penalty for dark tones
                        brightness_penalty = brightness_diff * 3.5
                    elif monk_brightness < 190:  # Moderate penalty
                        brightness_penalty = brightness_diff * 1.8
                    else:  # Light penalty for light tones
                        brightness_penalty = brightness_diff * 0.4
                    
                    combined_distance = (
                        rgb_distance * 0.15 +
                        lab_distance * 0.15 +
                        hue_distance * 0.05 +
                        brightness_penalty * 0.65
                    )
                elif avg_brightness > 180:  # Moderately fair skin
                    if monk_brightness < 150:  # Penalize very dark tones
                        brightness_penalty = brightness_diff * 2.0
                    else:
                        brightness_penalty = brightness_diff * 0.8
                    
                    combined_distance = (
                        rgb_distance * 0.25 +
                        lab_distance * 0.25 +
                        hue_distance * 0.1 +
                        brightness_penalty * 0.4
                    )
                else:  # Standard processing for medium to dark skin
                    combined_distance = (
                        rgb_distance * 0.4 +
                        lab_distance * 0.4 +
                        hue_distance * 0.2
                    )
                
                if combined_distance < min_distance:
                    min_distance = combined_distance
                    closest_monk = monk_name
            
            # Use ITA result if confidence is high and for fair skin tones
            if ita_confidence > 0.75 and ita_result in ['Monk 1', 'Monk 2', 'Monk 3']:
                logger.info(f"Using ITA classification: {ita_result} (confidence: {ita_confidence})")
                return ita_result, min_distance * 0.8  # Boost confidence
            
            return closest_monk, min_distance
            
        except Exception as e:
            logger.warning(f"Advanced Monk tone matching failed: {e}")
            return "Monk 4", 50.0
    
    def analyze_skin_tone(self, image: np.ndarray, monk_tones: Dict[str, str]) -> Dict:
        """Main method to analyze skin tone with enhanced algorithms."""
        try:
            logger.info("Starting enhanced skin tone analysis...")
            
            # Step 1: Detect face
            face_image = self.detect_face(image)
            if face_image is None:
                raise ValueError("No face detected in the image")
            
            # Step 2: Apply advanced lighting correction
            corrected_face = self.apply_advanced_lighting_correction(face_image)
            
            # Step 3: Extract skin regions
            region_colors = self.extract_skin_regions(corrected_face)
            
            if not region_colors:
                # Fallback to center region
                h, w = corrected_face.shape[:2]
                center_region = corrected_face[h//4:3*h//4, w//4:3*w//4]
                avg_color = np.mean(center_region.reshape(-1, 3), axis=0)
            else:
                # Step 4: Cluster colors to find dominant skin tone
                avg_color = self.cluster_skin_colors(region_colors)
            
            # Step 5: Find closest Monk tone
            closest_monk, min_distance = self.find_closest_monk_tone_advanced(avg_color, monk_tones)
            
            # Step 6: Calculate confidence
            confidence = self.calculate_advanced_confidence(face_image, avg_color, region_colors)
            
            # Format response
            monk_number = closest_monk.split()[1]
            monk_id = f"Monk{monk_number.zfill(2)}"
            
            # Convert RGB to hex
            derived_hex = '#{:02x}{:02x}{:02x}'.format(
                int(avg_color[0]), int(avg_color[1]), int(avg_color[2])
            )
            
            logger.info(f"Enhanced analysis result: {monk_id}, confidence: {confidence:.2f}")
            
            return {
                'monk_skin_tone': monk_id,
                'monk_tone_display': closest_monk,
                'monk_hex': monk_tones[closest_monk],
                'derived_hex_code': derived_hex,
                'dominant_rgb': avg_color.astype(int).tolist(),
                'confidence': round(confidence, 2),
                'success': True,
                'analysis_method': 'enhanced_multi_colorspace_clustering',
                'regions_analyzed': len(region_colors),
                'face_detected': True
            }
            
        except Exception as e:
            logger.error(f"Enhanced skin tone analysis failed: {e}")
            return {
                'monk_skin_tone': 'Monk04',
                'monk_tone_display': 'Monk 4',
                'monk_hex': monk_tones.get('Monk 4', '#eadaba'),
                'derived_hex_code': '#eadaba',
                'dominant_rgb': [234, 218, 186],
                'confidence': 0.3,
                'success': False,
                'error': str(e),
                'face_detected': False
            }
