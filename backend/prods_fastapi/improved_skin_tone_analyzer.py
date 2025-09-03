import cv2
import numpy as np
import mediapipe as mp
from sklearn.cluster import KMeans
from scipy import stats
import logging
from typing import List, Dict, Tuple, Optional
from scipy.spatial.distance import euclidean
from sklearn.preprocessing import normalize
import colorsys
import json

try:
    import dlib
    DLIB_AVAILABLE = True
except ImportError:
    dlib = None
    DLIB_AVAILABLE = False

logger = logging.getLogger(__name__)

class ImprovedSkinToneAnalyzer:
    def __init__(self):
        """Initialize the improved skin tone analyzer with enhanced algorithms."""
        # MediaPipe face detection and mesh
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing = mp.solutions.drawing_utils
        self.mediapipe_available = True
        
        # Enhanced face mesh for precise landmark detection
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        
        logger.info("MediaPipe face detection and mesh initialized successfully")
        
        # Dlib face detection (fallback)
        if DLIB_AVAILABLE:
            self.dlib_detector = dlib.get_frontal_face_detector()
            try:
                self.dlib_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")
                self.dlib_available = True
                logger.info("Dlib shape predictor loaded successfully")
            except Exception as e:
                self.dlib_predictor = None
                self.dlib_available = False
                logger.warning(f"Dlib shape predictor not available: {e}")
        else:
            self.dlib_detector = None
            self.dlib_predictor = None
            self.dlib_available = False
            logger.info("Dlib not installed, using MediaPipe only")

        # Enhanced skin color ranges for different conditions
        self.skin_color_ranges = {
            'ycrcb_narrow': {'lower': np.array([0, 133, 77]), 'upper': np.array([255, 173, 127])},
            'ycrcb_wide': {'lower': np.array([0, 125, 70]), 'upper': np.array([255, 180, 135])},
            'hsv_range': {'lower': np.array([0, 20, 70]), 'upper': np.array([20, 255, 255])},
            'lab_range': {'lower': np.array([20, 15, 15]), 'upper': np.array([95, 127, 127])}
        }

    def detect_face_landmarks_mediapipe(self, image: np.ndarray) -> Optional[List]:
        """Detect face landmarks using MediaPipe face mesh for precise region extraction."""
        if not self.mediapipe_available:
            return None
        
        try:
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = self.face_mesh.process(rgb_image)
            
            if results.multi_face_landmarks:
                landmarks = results.multi_face_landmarks[0]
                h, w, _ = image.shape
                
                # Convert normalized landmarks to pixel coordinates
                landmark_points = []
                for landmark in landmarks.landmark:
                    x = int(landmark.x * w)
                    y = int(landmark.y * h)
                    landmark_points.append((x, y))
                
                return landmark_points
        except Exception as e:
            logger.warning(f"MediaPipe face mesh failed: {e}")
        
        return None

    def extract_precise_skin_regions(self, image: np.ndarray, landmarks: Optional[List] = None) -> List[np.ndarray]:
        """Extract skin regions using facial landmarks for precise area selection."""
        h, w = image.shape[:2]
        
        if landmarks and len(landmarks) >= 468:  # MediaPipe face mesh has 468 landmarks
            region_colors = []
            
            try:
                # Define landmark indices for different face regions
                # These are based on MediaPipe face mesh topology
                forehead_indices = [9, 10, 151, 337, 299, 333, 298, 301]
                left_cheek_indices = [116, 117, 118, 119, 120, 121, 126, 142]
                right_cheek_indices = [345, 346, 347, 348, 349, 350, 355, 371]
                nose_bridge_indices = [6, 51, 48, 115, 131, 134, 102, 49, 220, 305, 331, 294]
                chin_indices = [18, 175, 199, 200, 9, 10, 151, 175]
                
                regions = {
                    'forehead': forehead_indices,
                    'left_cheek': left_cheek_indices,
                    'right_cheek': right_cheek_indices,
                    'nose_bridge': nose_bridge_indices,
                    'chin': chin_indices
                }
                
                for region_name, indices in regions.items():
                    # Create polygon mask for the region
                    points = []
                    for idx in indices:
                        if idx < len(landmarks):
                            points.append(landmarks[idx])
                    
                    if len(points) >= 3:
                        # Create mask for the region
                        mask = np.zeros((h, w), dtype=np.uint8)
                        points_array = np.array(points, dtype=np.int32)
                        cv2.fillPoly(mask, [points_array], 255)
                        
                        # Extract pixels from the masked region
                        region_pixels = image[mask > 0]
                        
                        if len(region_pixels) > 50:
                            # Apply skin color filtering
                            filtered_pixels = self.apply_skin_color_filter(region_pixels)
                            if len(filtered_pixels) > 20:
                                region_color = np.mean(filtered_pixels, axis=0)
                                region_colors.append(region_color)
                
                return region_colors
                
            except Exception as e:
                logger.warning(f"Landmark-based region extraction failed: {e}")
        
        # Fallback to geometric regions
        return self.extract_geometric_skin_regions(image)

    def extract_geometric_skin_regions(self, face_image: np.ndarray) -> List[np.ndarray]:
        """Fallback method for skin region extraction using geometric approach."""
        h, w = face_image.shape[:2]
        
        # Define skin regions with improved proportions
        regions = {
            'forehead': (int(0.15*w), int(0.08*h), int(0.7*w), int(0.25*h)),
            'left_cheek': (int(0.05*w), int(0.3*h), int(0.4*w), int(0.35*h)),
            'right_cheek': (int(0.55*w), int(0.3*h), int(0.4*w), int(0.35*h)),
            'nose_bridge': (int(0.35*w), int(0.25*h), int(0.3*w), int(0.35*h)),
            'chin': (int(0.25*w), int(0.65*h), int(0.5*w), int(0.25*h)),
            'upper_neck': (int(0.3*w), int(0.85*h), int(0.4*w), int(0.15*h))
        }
        
        region_colors = []
        
        for region_name, (x, y, rw, rh) in regions.items():
            if x + rw <= w and y + rh <= h and x >= 0 and y >= 0:
                region = face_image[y:y+rh, x:x+rw]
                
                if region.size > 100:
                    # Apply skin color filtering
                    filtered_pixels = self.apply_skin_color_filter(region.reshape(-1, 3))
                    
                    if len(filtered_pixels) > 20:
                        region_color = np.mean(filtered_pixels, axis=0)
                        region_colors.append(region_color)
        
        return region_colors

    def apply_skin_color_filter(self, pixels: np.ndarray) -> np.ndarray:
        """Apply multiple skin color filters to extract skin pixels."""
        if len(pixels.shape) == 1:
            pixels = pixels.reshape(-1, 3)
        
        # Convert to different color spaces for filtering
        try:
            # YCrCb filtering (most reliable for skin detection)
            ycrcb_pixels = cv2.cvtColor(pixels.reshape(1, -1, 3), cv2.COLOR_RGB2YCrCb).reshape(-1, 3)
            ycrcb_mask = cv2.inRange(ycrcb_pixels, 
                                   self.skin_color_ranges['ycrcb_narrow']['lower'],
                                   self.skin_color_ranges['ycrcb_narrow']['upper'])
            
            # HSV filtering for additional validation
            hsv_pixels = cv2.cvtColor(pixels.reshape(1, -1, 3), cv2.COLOR_RGB2HSV).reshape(-1, 3)
            hsv_mask = cv2.inRange(hsv_pixels,
                                 self.skin_color_ranges['hsv_range']['lower'],
                                 self.skin_color_ranges['hsv_range']['upper'])
            
            # Combine masks (use OR for broader detection)
            combined_mask = cv2.bitwise_or(ycrcb_mask, hsv_mask)
            
            # Apply brightness-based filtering
            brightness = np.mean(pixels, axis=1)
            brightness_mask = (brightness > 50) & (brightness < 240)  # Avoid very dark/bright pixels
            
            # Final mask combination
            final_mask = combined_mask.flatten() & brightness_mask
            
            if np.sum(final_mask) > 10:
                return pixels[final_mask]
            else:
                # If too restrictive, use wider YCrCb range
                wide_ycrcb_mask = cv2.inRange(ycrcb_pixels,
                                            self.skin_color_ranges['ycrcb_wide']['lower'],
                                            self.skin_color_ranges['ycrcb_wide']['upper'])
                wide_final_mask = wide_ycrcb_mask.flatten() & brightness_mask
                
                if np.sum(wide_final_mask) > 5:
                    return pixels[wide_final_mask]
                else:
                    # Last resort: return brightest pixels
                    top_bright_indices = np.argsort(brightness)[-min(50, len(brightness)):]
                    return pixels[top_bright_indices]
        
        except Exception as e:
            logger.warning(f"Skin color filtering failed: {e}")
            return pixels

    def enhanced_lighting_correction(self, image: np.ndarray) -> np.ndarray:
        """Enhanced lighting correction with adaptive parameters."""
        try:
            # Convert to LAB color space
            lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)
            
            # Adaptive CLAHE based on image characteristics
            mean_brightness = np.mean(l)
            std_brightness = np.std(l)
            
            # Adjust CLAHE parameters based on image statistics
            if mean_brightness < 80:  # Dark image
                clip_limit = 4.0
                tile_grid_size = (6, 6)
            elif mean_brightness > 180:  # Bright image
                clip_limit = 2.0
                tile_grid_size = (10, 10)
            else:  # Normal image
                clip_limit = 3.0
                tile_grid_size = (8, 8)
            
            # Apply adaptive CLAHE
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=tile_grid_size)
            l_corrected = clahe.apply(l)
            
            # Merge back
            lab_corrected = cv2.merge([l_corrected, a, b])
            rgb_corrected = cv2.cvtColor(lab_corrected, cv2.COLOR_LAB2RGB)
            
            # Adaptive gamma correction
            gamma = self.calculate_adaptive_gamma(rgb_corrected, mean_brightness, std_brightness)
            
            if gamma != 1.0:
                rgb_corrected = np.power(rgb_corrected / 255.0, gamma) * 255.0
                rgb_corrected = np.clip(rgb_corrected, 0, 255).astype(np.uint8)
            
            # White balance correction for skin tones
            rgb_corrected = self.apply_white_balance_correction(rgb_corrected)
            
            return rgb_corrected
            
        except Exception as e:
            logger.warning(f"Enhanced lighting correction failed: {e}")
            return image

    def calculate_adaptive_gamma(self, image: np.ndarray, mean_brightness: float, std_brightness: float) -> float:
        """Calculate adaptive gamma value based on image characteristics."""
        # Base gamma on overall image statistics
        if mean_brightness < 60:  # Very dark
            gamma = 1.6
        elif mean_brightness < 100:  # Dark
            gamma = 1.3
        elif mean_brightness < 140:  # Medium-dark
            gamma = 1.1
        elif mean_brightness < 180:  # Medium
            gamma = 1.0
        elif mean_brightness < 220:  # Bright
            gamma = 0.9
        else:  # Very bright
            gamma = 0.8
        
        # Adjust based on contrast (std deviation)
        if std_brightness < 20:  # Low contrast
            gamma *= 1.1  # Increase gamma for low contrast
        elif std_brightness > 60:  # High contrast
            gamma *= 0.9  # Decrease gamma for high contrast
        
        return gamma

    def apply_white_balance_correction(self, image: np.ndarray) -> np.ndarray:
        """Apply white balance correction optimized for skin tones."""
        try:
            # Simple gray world assumption with skin tone bias
            mean_r = np.mean(image[:, :, 0])
            mean_g = np.mean(image[:, :, 1])
            mean_b = np.mean(image[:, :, 2])
            
            # Target gray value (slightly warm for skin tones)
            target_gray = 128
            
            # Calculate correction factors
            r_factor = target_gray / mean_r if mean_r > 0 else 1.0
            g_factor = target_gray / mean_g if mean_g > 0 else 1.0
            b_factor = target_gray / mean_b if mean_b > 0 else 1.0
            
            # Limit correction factors to avoid over-correction
            r_factor = np.clip(r_factor, 0.7, 1.5)
            g_factor = np.clip(g_factor, 0.7, 1.5)
            b_factor = np.clip(b_factor, 0.7, 1.5)
            
            # Apply correction
            corrected = image.astype(np.float32)
            corrected[:, :, 0] *= r_factor
            corrected[:, :, 1] *= g_factor
            corrected[:, :, 2] *= b_factor
            
            return np.clip(corrected, 0, 255).astype(np.uint8)
            
        except Exception as e:
            logger.warning(f"White balance correction failed: {e}")
            return image

    def advanced_color_clustering(self, region_colors: List[np.ndarray], n_clusters: int = 4) -> Tuple[np.ndarray, float]:
        """Enhanced color clustering with outlier detection and confidence scoring."""
        if not region_colors:
            return np.array([220, 210, 200]), 0.3
        
        try:
            all_colors = np.vstack(region_colors)
            n_colors = len(all_colors)
            
            if n_colors < 3:
                return np.mean(all_colors, axis=0), 0.4
            
            # Remove outliers using IQR method
            cleaned_colors = self.remove_color_outliers(all_colors)
            
            if len(cleaned_colors) < 2:
                cleaned_colors = all_colors  # Fallback if too many outliers removed
            
            # Apply K-means clustering
            k = min(n_clusters, len(cleaned_colors))
            kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
            kmeans.fit(cleaned_colors)
            
            # Find the cluster center closest to the median color
            median_color = np.median(cleaned_colors, axis=0)
            distances = [np.linalg.norm(center - median_color) for center in kmeans.cluster_centers_]
            best_cluster_idx = np.argmin(distances)
            final_color = kmeans.cluster_centers_[best_cluster_idx]
            
            # Calculate clustering confidence
            cluster_confidence = self.calculate_clustering_confidence(cleaned_colors, kmeans, best_cluster_idx)
            
            return final_color, cluster_confidence
            
        except Exception as e:
            logger.warning(f"Advanced color clustering failed: {e}")
            return np.mean(region_colors, axis=0) if region_colors else np.array([200, 180, 160]), 0.3

    def remove_color_outliers(self, colors: np.ndarray) -> np.ndarray:
        """Remove color outliers using statistical methods."""
        try:
            # Calculate brightness for each color
            brightness = np.mean(colors, axis=1)
            
            # Use IQR method for outlier detection
            Q1 = np.percentile(brightness, 25)
            Q3 = np.percentile(brightness, 75)
            IQR = Q3 - Q1
            
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Keep colors within bounds
            mask = (brightness >= lower_bound) & (brightness <= upper_bound)
            cleaned_colors = colors[mask]
            
            # Ensure we don't remove too many colors
            if len(cleaned_colors) < len(colors) * 0.5:
                # If more than half are considered outliers, use less strict bounds
                lower_bound = Q1 - 2.5 * IQR
                upper_bound = Q3 + 2.5 * IQR
                mask = (brightness >= lower_bound) & (brightness <= upper_bound)
                cleaned_colors = colors[mask]
            
            return cleaned_colors if len(cleaned_colors) > 0 else colors
            
        except Exception as e:
            logger.warning(f"Outlier removal failed: {e}")
            return colors

    def calculate_clustering_confidence(self, colors: np.ndarray, kmeans, best_cluster_idx: int) -> float:
        """Calculate confidence score for clustering results."""
        try:
            labels = kmeans.labels_
            centers = kmeans.cluster_centers_
            
            # Silhouette-like score for best cluster
            best_cluster_mask = labels == best_cluster_idx
            best_cluster_colors = colors[best_cluster_mask]
            
            if len(best_cluster_colors) < 2:
                return 0.3
            
            # Intra-cluster distance (smaller is better)
            intra_distances = [np.linalg.norm(color - centers[best_cluster_idx]) 
                             for color in best_cluster_colors]
            avg_intra_distance = np.mean(intra_distances)
            
            # Inter-cluster distance (larger is better)
            inter_distances = []
            for i, center in enumerate(centers):
                if i != best_cluster_idx:
                    inter_distances.append(np.linalg.norm(centers[best_cluster_idx] - center))
            
            avg_inter_distance = np.mean(inter_distances) if inter_distances else avg_intra_distance * 2
            
            # Calculate confidence (0-1 scale)
            if avg_inter_distance > 0:
                silhouette_score = (avg_inter_distance - avg_intra_distance) / max(avg_inter_distance, avg_intra_distance)
                confidence = max(0, min(1, (silhouette_score + 1) / 2))  # Normalize to 0-1
            else:
                confidence = 0.5
            
            return confidence
            
        except Exception as e:
            logger.warning(f"Clustering confidence calculation failed: {e}")
            return 0.5

    def analyze_skin_tone_enhanced(self, image: np.ndarray, monk_tones: Dict[str, str]) -> Dict:
        """Enhanced skin tone analysis with all improvements."""
        try:
            logger.info("Starting enhanced skin tone analysis...")
            
            # Step 1: Detect face and landmarks
            face_image = self.detect_face(image)
            if face_image is None:
                raise ValueError("No face detected in the image")
            
            # Try to get precise landmarks
            landmarks = self.detect_face_landmarks_mediapipe(face_image)
            
            # Step 2: Apply enhanced lighting correction
            corrected_face = self.enhanced_lighting_correction(face_image)
            
            # Step 3: Extract skin regions (with landmarks if available)
            if landmarks:
                region_colors = self.extract_precise_skin_regions(corrected_face, landmarks)
                logger.info(f"Using landmark-based region extraction: {len(region_colors)} regions")
            else:
                region_colors = self.extract_geometric_skin_regions(corrected_face)
                logger.info(f"Using geometric region extraction: {len(region_colors)} regions")
            
            if not region_colors:
                # Ultimate fallback to center region
                h, w = corrected_face.shape[:2]
                center_region = corrected_face[h//4:3*h//4, w//4:3*w//4]
                center_pixels = self.apply_skin_color_filter(center_region.reshape(-1, 3))
                avg_color = np.mean(center_pixels, axis=0) if len(center_pixels) > 0 else np.mean(center_region.reshape(-1, 3), axis=0)
                clustering_confidence = 0.3
            else:
                # Step 4: Advanced color clustering
                avg_color, clustering_confidence = self.advanced_color_clustering(region_colors)
            
            # Step 5: Find closest Monk tone with enhanced algorithm
            closest_monk, min_distance = self.find_closest_monk_tone_advanced(avg_color, monk_tones)
            
            # Step 6: Calculate comprehensive confidence
            final_confidence = self.calculate_comprehensive_confidence(
                face_image, avg_color, region_colors, clustering_confidence, min_distance, landmarks is not None
            )
            
            # Format response
            monk_number = closest_monk.split()[1]
            monk_id = f"Monk{monk_number.zfill(2)}"
            
            # Convert RGB to hex
            derived_hex = '#{:02x}{:02x}{:02x}'.format(
                int(avg_color[0]), int(avg_color[1]), int(avg_color[2])
            )
            
            logger.info(f"Enhanced analysis result: {monk_id}, confidence: {final_confidence:.2f}")
            
            return {
                'monk_skin_tone': monk_id,
                'monk_tone_display': closest_monk,
                'monk_hex': monk_tones[closest_monk],
                'derived_hex_code': derived_hex,
                'dominant_rgb': avg_color.astype(int).tolist(),
                'confidence': round(final_confidence, 2),
                'success': True,
                'analysis_method': 'enhanced_landmark_clustering',
                'regions_analyzed': len(region_colors),
                'face_detected': True,
                'landmarks_detected': landmarks is not None,
                'clustering_confidence': round(clustering_confidence, 2)
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
                'face_detected': False,
                'landmarks_detected': False
            }

    def calculate_comprehensive_confidence(self, face_image: np.ndarray, final_color: np.ndarray, 
                                         region_colors: List[np.ndarray], clustering_confidence: float,
                                         color_distance: float, has_landmarks: bool) -> float:
        """Calculate comprehensive confidence score."""
        try:
            confidence_factors = []
            
            # 1. Clustering confidence (25%)
            confidence_factors.append(clustering_confidence * 0.25)
            
            # 2. Color consistency across regions (20%)
            if len(region_colors) > 1:
                color_variations = [np.std(color) for color in region_colors]
                consistency_score = max(0, 1 - (np.mean(color_variations) / 30))
                confidence_factors.append(consistency_score * 0.20)
            else:
                confidence_factors.append(0.10)  # Partial score for single region
            
            # 3. Image quality factors (20%)
            gray = cv2.cvtColor(face_image, cv2.COLOR_RGB2GRAY)
            sharpness = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(1.0, sharpness / 500)
            confidence_factors.append(sharpness_score * 0.20)
            
            # 4. Color distance from Monk tones (15%)
            distance_score = max(0, 1 - (color_distance / 150))
            confidence_factors.append(distance_score * 0.15)
            
            # 5. Landmark detection bonus (10%)
            landmark_bonus = 0.10 if has_landmarks else 0.05
            confidence_factors.append(landmark_bonus)
            
            # 6. Color validity (skin-like colors) (10%)
            skin_validity = self.validate_skin_color(final_color)
            confidence_factors.append(skin_validity * 0.10)
            
            final_confidence = sum(confidence_factors)
            return min(1.0, final_confidence)
            
        except Exception as e:
            logger.warning(f"Comprehensive confidence calculation failed: {e}")
            return 0.5

    def validate_skin_color(self, color: np.ndarray) -> float:
        """Validate if the detected color is skin-like."""
        try:
            r, g, b = color
            
            # Check if color is within typical skin color ranges
            # Convert to HSV for hue checking
            hsv = cv2.cvtColor(np.uint8([[[r, g, b]]]), cv2.COLOR_RGB2HSV)[0][0]
            h, s, v = hsv
            
            # Skin typically has hue in range 0-30 (red-yellow spectrum)
            hue_valid = (h <= 30) or (h >= 330)
            
            # Skin has moderate saturation (not gray, not oversaturated)
            sat_valid = 20 <= s <= 200
            
            # Skin has reasonable brightness
            brightness_valid = 50 <= v <= 240
            
            # Check RGB ratios (skin typically has R > G > B)
            ratio_valid = r >= g >= b * 0.8  # Allow some flexibility
            
            # Count valid criteria
            valid_count = sum([hue_valid, sat_valid, brightness_valid, ratio_valid])
            
            return valid_count / 4.0  # Return as proportion
            
        except Exception as e:
            logger.warning(f"Skin color validation failed: {e}")
            return 0.5

    # Include the previous methods for face detection and Monk tone matching
    def detect_face(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Detect face using MediaPipe and return face region."""
        try:
            with self.mp_face_detection.FaceDetection(
                model_selection=1, min_detection_confidence=0.7) as face_detection:
                
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                results = face_detection.process(rgb_image)
                
                if results.detections:
                    detection = results.detections[0]
                    bboxC = detection.location_data.relative_bounding_box
                    ih, iw, _ = image.shape
                    
                    x = int(bboxC.xmin * iw)
                    y = int(bboxC.ymin * ih)
                    w = int(bboxC.width * iw)
                    h = int(bboxC.height * ih)
                    
                    # Add padding
                    padding = 0.1
                    x = max(0, int(x - w * padding))
                    y = max(0, int(y - h * padding))
                    w = min(iw - x, int(w * (1 + 2 * padding)))
                    h = min(ih - y, int(h * (1 + 2 * padding)))
                    
                    face_region = image[y:y+h, x:x+w]
                    
                    if face_region.shape[0] >= 50 and face_region.shape[1] >= 50:
                        return face_region
        
        except Exception as e:
            logger.warning(f"Face detection failed: {e}")
        
        return None

    def find_closest_monk_tone_advanced(self, rgb_color: np.ndarray, monk_tones: Dict[str, str]) -> Tuple[str, float]:
        """Advanced Monk tone matching with multiple color space analysis."""
        try:
            # Method 1: ITA-based classification
            ita_result, ita_confidence = self.advanced_skin_tone_classification(rgb_color)
            
            # Method 2: Multi-color space distance calculation
            avg_brightness = np.mean(rgb_color)
            lab_color = cv2.cvtColor(np.uint8([[rgb_color]]), cv2.COLOR_RGB2LAB)[0][0]
            hsv_color = cv2.cvtColor(np.uint8([[rgb_color]]), cv2.COLOR_RGB2HSV)[0][0]
            
            min_distance = float('inf')
            closest_monk = "Monk 4"  # Default
            
            for monk_name, hex_color in monk_tones.items():
                monk_rgb = np.array([
                    int(hex_color[1:3], 16),
                    int(hex_color[3:5], 16),
                    int(hex_color[5:7], 16)
                ])
                
                monk_lab = cv2.cvtColor(np.uint8([[monk_rgb]]), cv2.COLOR_RGB2LAB)[0][0]
                monk_hsv = cv2.cvtColor(np.uint8([[monk_rgb]]), cv2.COLOR_RGB2HSV)[0][0]
                
                # Calculate distances
                rgb_distance = np.sqrt(np.sum((rgb_color - monk_rgb) ** 2))
                lab_distance = np.sqrt(np.sum((lab_color - monk_lab) ** 2))
                
                # Hue distance (circular)
                hue_diff = min(abs(hsv_color[0] - monk_hsv[0]), 
                             360 - abs(hsv_color[0] - monk_hsv[0]))
                hue_distance = hue_diff / 180.0 * 100
                
                brightness_diff = abs(avg_brightness - np.mean(monk_rgb))
                
                # Enhanced distance calculation with adaptive weighting
                if avg_brightness > 200:  # Very fair skin
                    combined_distance = (
                        rgb_distance * 0.2 +
                        lab_distance * 0.3 +
                        hue_distance * 0.1 +
                        brightness_diff * 1.2
                    )
                elif avg_brightness > 160:  # Fair skin
                    combined_distance = (
                        rgb_distance * 0.3 +
                        lab_distance * 0.4 +
                        hue_distance * 0.1 +
                        brightness_diff * 0.8
                    )
                else:  # Medium to dark skin
                    combined_distance = (
                        rgb_distance * 0.4 +
                        lab_distance * 0.4 +
                        hue_distance * 0.2 +
                        brightness_diff * 0.4
                    )
                
                if combined_distance < min_distance:
                    min_distance = combined_distance
                    closest_monk = monk_name
            
            # Use ITA result for light skin tones with high confidence
            if ita_confidence > 0.7 and ita_result in ['Monk 1', 'Monk 2', 'Monk 3']:
                return ita_result, min_distance * 0.8
            
            return closest_monk, min_distance
            
        except Exception as e:
            logger.warning(f"Advanced Monk tone matching failed: {e}")
            return "Monk 4", 50.0

    def advanced_skin_tone_classification(self, rgb_color: np.ndarray) -> Tuple[str, float]:
        """ITA-based skin tone classification."""
        try:
            r, g, b = rgb_color
            
            # Calculate Individual Typology Angle (ITA)
            lab = cv2.cvtColor(np.uint8([[[r, g, b]]]), cv2.COLOR_RGB2LAB)[0][0]
            L, a_val, b_val = lab
            
            if b_val != 0:
                ita = np.arctan((L - 50) / b_val) * 180 / np.pi
            else:
                ita = 90 if L > 50 else -90
            
            # ITA-based classification
            if ita > 55:
                return "Monk 1", 0.9
            elif ita > 41:
                return "Monk 2", 0.85
            elif ita > 28:
                return "Monk 3", 0.8
            elif ita > 10:
                return "Monk 4", 0.75
            elif ita > -30:
                if L > 65:
                    return "Monk 5", 0.7
                elif L > 55:
                    return "Monk 6", 0.7
                else:
                    return "Monk 7", 0.7
            else:
                if L > 45:
                    return "Monk 8", 0.65
                elif L > 35:
                    return "Monk 9", 0.65
                else:
                    return "Monk 10", 0.65
                    
        except Exception as e:
            logger.warning(f"ITA classification failed: {e}")
            return "Monk 4", 0.5
