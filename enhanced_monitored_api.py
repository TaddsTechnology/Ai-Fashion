"""
Enhanced API endpoints with comprehensive Sentry monitoring
This shows how to integrate Sentry monitoring into your existing endpoints
"""

from fastapi import FastAPI, HTTPException, File, UploadFile
from services.sentry_service import EnhancedSentryService
from services.cloudinary_service import cloudinary_service
from enhanced_skin_tone_analyzer import EnhancedSkinToneAnalyzer
import time
import logging
from typing import Dict, Any
import hashlib

logger = logging.getLogger(__name__)

# Enhanced skin tone analysis endpoint with comprehensive monitoring
@EnhancedSentryService.monitor_api_endpoint("analyze_skin_tone_monitored")
async def analyze_skin_tone_monitored(file: UploadFile = File(...)):
    """
    Enhanced skin tone analysis with comprehensive Sentry monitoring.
    
    This endpoint demonstrates:
    1. Performance monitoring
    2. Error tracking with context
    3. User journey tracking
    4. Business metrics capture
    5. Custom event logging
    """
    start_time = time.time()
    user_id = None
    
    try:
        # Validate file
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload an image."
            )
        
        # Read image data
        image_data = await file.read()
        
        # Generate user ID for tracking (in real app, get from authentication)
        user_id = hashlib.md5(str(len(image_data)).encode()).hexdigest()[:8]
        
        # Track user journey
        EnhancedSentryService.track_user_journey(
            user_id=user_id,
            action="skin_tone_analysis_started",
            metadata={
                "file_size": len(image_data),
                "file_type": file.content_type,
                "filename": file.filename
            }
        )
        
        # Upload to Cloudinary with monitoring
        upload_result = await cloudinary_service.upload_image(
            image_data=image_data,
            folder='skin_tone_analysis',
            tags=['analysis', 'monitored']
        )
        
        # Capture Cloudinary upload event
        EnhancedSentryService.capture_cloudinary_upload(
            public_id=upload_result.get('public_id', 'unknown'),
            upload_result=upload_result
        )
        
        if not upload_result.get('success'):
            raise Exception(f"Cloudinary upload failed: {upload_result.get('error')}")
        
        # Initialize analyzer
        analyzer = EnhancedSkinToneAnalyzer()
        
        # Run skin tone analysis
        from PIL import Image
        import numpy as np
        import io
        
        image = Image.open(io.BytesIO(image_data))
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image_array = np.array(image)
        
        # Monk skin tones
        MONK_SKIN_TONES = {
            'Monk 1': '#f6ede4', 'Monk 2': '#f3e7db', 'Monk 3': '#f7ead0',
            'Monk 4': '#eadaba', 'Monk 5': '#d7bd96', 'Monk 6': '#a07e56',
            'Monk 7': '#825c43', 'Monk 8': '#604134', 'Monk 9': '#3a312a',
            'Monk 10': '#292420'
        }
        
        analysis_result = analyzer.analyze_skin_tone(image_array, MONK_SKIN_TONES)
        processing_time = time.time() - start_time
        analysis_result['processing_time'] = processing_time
        
        # Capture skin tone analysis event
        EnhancedSentryService.capture_skin_tone_analysis(
            user_id=user_id,
            image_data={
                'size': len(image_data),
                'format': file.content_type,
                'dimensions': f"{image.width}x{image.height}"
            },
            result=analysis_result
        )
        
        # Capture business metrics
        EnhancedSentryService.capture_business_metric(
            metric_name="skin_tone_analysis_success_rate",
            value=1.0 if analysis_result.get('success') else 0.0,
            tags={
                "monk_tone": analysis_result.get('monk_skin_tone', 'unknown'),
                "confidence_level": "high" if analysis_result.get('confidence', 0) > 0.7 else "low"
            }
        )
        
        # Capture performance metric
        EnhancedSentryService.capture_business_metric(
            metric_name="analysis_processing_time",
            value=processing_time,
            tags={"endpoint": "skin_tone_analysis"}
        )
        
        # Track successful completion
        EnhancedSentryService.track_user_journey(
            user_id=user_id,
            action="skin_tone_analysis_completed",
            metadata={
                "monk_tone": analysis_result.get('monk_skin_tone'),
                "confidence": analysis_result.get('confidence'),
                "processing_time": processing_time
            }
        )
        
        # Enhanced response with monitoring metadata
        response = {
            **analysis_result,
            'cloudinary_url': upload_result.get('url'),
            'cloudinary_public_id': upload_result.get('public_id'),
            'processing_time': processing_time,
            'user_session': user_id,
            'monitoring_enabled': True
        }
        
        logger.info(f"Monitored analysis completed: {analysis_result.get('monk_skin_tone')} "
                   f"(confidence: {analysis_result.get('confidence')}, time: {processing_time:.2f}s)")
        
        return response
        
    except HTTPException:
        # Track user journey for HTTP errors
        if user_id:
            EnhancedSentryService.track_user_journey(
                user_id=user_id,
                action="analysis_failed_validation",
                metadata={"error_type": "validation"}
            )
        raise
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        # Track user journey for unexpected errors
        if user_id:
            EnhancedSentryService.track_user_journey(
                user_id=user_id,
                action="analysis_failed_error",
                metadata={
                    "error_type": "unexpected",
                    "processing_time": processing_time
                }
            )
        
        # Capture business metric for failures
        EnhancedSentryService.capture_business_metric(
            metric_name="skin_tone_analysis_success_rate",
            value=0.0,
            tags={
                "error_type": type(e).__name__,
                "processing_time": f"{processing_time:.2f}s"
            }
        )
        
        logger.error(f"Monitored skin tone analysis failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'monk_skin_tone': 'Monk04',
            'confidence': 0.0,
            'processing_time': processing_time,
            'user_session': user_id,
            'monitoring_enabled': True,
            'fallback': True
        }


@EnhancedSentryService.monitor_api_endpoint("batch_analysis")
async def batch_analyze_with_monitoring(files: list[UploadFile] = File(...)):
    """
    Batch analysis with comprehensive monitoring for training data collection.
    """
    start_time = time.time()
    
    try:
        if len(files) > 10:
            raise HTTPException(
                status_code=400,
                detail="Maximum 10 images allowed per batch"
            )
        
        batch_id = hashlib.md5(str(int(start_time)).encode()).hexdigest()[:8]
        
        # Track batch analysis start
        EnhancedSentryService.track_user_journey(
            user_id=f"batch_{batch_id}",
            action="batch_analysis_started",
            metadata={
                "batch_size": len(files),
                "batch_id": batch_id
            }
        )
        
        results = []
        successful_analyses = 0
        
        for i, file in enumerate(files):
            try:
                if not file.content_type or not file.content_type.startswith('image/'):
                    continue
                
                # Analyze individual image (simplified for demo)
                image_data = await file.read()
                
                # Mock analysis result for demo
                result = {
                    'batch_index': i,
                    'filename': file.filename,
                    'success': True,
                    'monk_skin_tone': f'Monk0{(i % 10) + 1}',
                    'confidence': 0.8 + (i * 0.02),
                    'size': len(image_data)
                }
                
                results.append(result)
                successful_analyses += 1
                
            except Exception as e:
                results.append({
                    'batch_index': i,
                    'filename': file.filename,
                    'success': False,
                    'error': str(e)
                })
        
        processing_time = time.time() - start_time
        
        # Capture batch metrics
        EnhancedSentryService.capture_business_metric(
            metric_name="batch_analysis_success_rate",
            value=successful_analyses / len(files) if files else 0,
            tags={
                "batch_size": len(files),
                "batch_id": batch_id
            }
        )
        
        EnhancedSentryService.capture_business_metric(
            metric_name="batch_processing_time",
            value=processing_time,
            tags={"batch_size": len(files)}
        )
        
        # Track completion
        EnhancedSentryService.track_user_journey(
            user_id=f"batch_{batch_id}",
            action="batch_analysis_completed",
            metadata={
                "successful_analyses": successful_analyses,
                "total_files": len(files),
                "processing_time": processing_time
            }
        )
        
        return {
            'success': True,
            'batch_id': batch_id,
            'total_files': len(files),
            'successful_analyses': successful_analyses,
            'processing_time': processing_time,
            'results': results,
            'monitoring_enabled': True
        }
        
    except Exception as e:
        processing_time = time.time() - start_time
        
        EnhancedSentryService.capture_business_metric(
            metric_name="batch_analysis_success_rate",
            value=0.0,
            tags={"error_type": type(e).__name__}
        )
        
        logger.error(f"Batch analysis failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'processing_time': processing_time,
            'monitoring_enabled': True
        }


# Custom endpoint to capture model performance metrics
@app.post("/model-performance")
async def record_model_performance(metrics: Dict[str, Any]):
    """
    Endpoint to record ML model performance metrics.
    """
    try:
        model_name = metrics.get('model_name', 'unknown')
        
        # Capture model performance
        EnhancedSentryService.capture_model_performance(
            model_name=model_name,
            metrics=metrics
        )
        
        # Capture individual metrics as business metrics
        for metric_name, value in metrics.items():
            if isinstance(value, (int, float)) and metric_name != 'model_name':
                EnhancedSentryService.capture_business_metric(
                    metric_name=f"model_{metric_name}",
                    value=float(value),
                    tags={"model": model_name}
                )
        
        return {
            'success': True,
            'message': 'Model performance metrics recorded',
            'model_name': model_name,
            'metrics_count': len(metrics)
        }
        
    except Exception as e:
        logger.error(f"Failed to record model performance: {e}")
        return {
            'success': False,
            'error': str(e)
        }


# Health check endpoint with monitoring
@app.get("/health-monitored")
async def health_check_monitored():
    """
    Health check endpoint with Sentry monitoring.
    """
    try:
        # Capture system health metrics
        import psutil
        
        cpu_percent = psutil.cpu_percent()
        memory_percent = psutil.virtual_memory().percent
        disk_percent = psutil.disk_usage('/').percent
        
        # Capture infrastructure metrics
        EnhancedSentryService.capture_business_metric(
            metric_name="system_cpu_usage",
            value=cpu_percent,
            tags={"component": "infrastructure"}
        )
        
        EnhancedSentryService.capture_business_metric(
            metric_name="system_memory_usage",
            value=memory_percent,
            tags={"component": "infrastructure"}
        )
        
        EnhancedSentryService.capture_business_metric(
            metric_name="system_disk_usage",
            value=disk_percent,
            tags={"component": "infrastructure"}
        )
        
        return {
            "status": "healthy",
            "message": "AI Fashion Backend is running with monitoring",
            "system_metrics": {
                "cpu_usage": f"{cpu_percent}%",
                "memory_usage": f"{memory_percent}%",
                "disk_usage": f"{disk_percent}%"
            },
            "monitoring_enabled": True
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "monitoring_enabled": True
        }
