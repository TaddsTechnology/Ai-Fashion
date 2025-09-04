"""
API Versioning System
Implements versioning strategy to prevent breaking changes
"""
import logging
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Header, HTTPException, Request
from fastapi.routing import APIRoute
from enum import Enum
from dataclasses import dataclass
from datetime import datetime, timedelta
import re

logger = logging.getLogger(__name__)

class APIVersion(str, Enum):
    """Supported API versions"""
    V1 = "v1"
    V2 = "v2"
    V3 = "v3"  # Future version

@dataclass
class VersionInfo:
    """API version information"""
    version: str
    release_date: datetime
    deprecated: bool = False
    deprecation_date: Optional[datetime] = None
    sunset_date: Optional[datetime] = None
    changelog: List[str] = None
    
    def __post_init__(self):
        if self.changelog is None:
            self.changelog = []

class APIVersioningManager:
    """
    Manages API versioning across the application
    """
    
    def __init__(self):
        self.versions = {
            APIVersion.V1: VersionInfo(
                version="v1",
                release_date=datetime(2024, 1, 1),
                deprecated=False,
                changelog=[
                    "Initial release",
                    "Basic color recommendations",
                    "Skin tone analysis",
                    "Simple health checks"
                ]
            ),
            APIVersion.V2: VersionInfo(
                version="v2",
                release_date=datetime(2024, 6, 1),
                deprecated=False,
                changelog=[
                    "Enhanced color recommendations",
                    "Multiple data sources",
                    "Improved error handling",
                    "Performance optimizations",
                    "Comprehensive monitoring"
                ]
            ),
            APIVersion.V3: VersionInfo(
                version="v3",
                release_date=datetime(2024, 12, 1),
                deprecated=False,
                changelog=[
                    "Machine learning integration",
                    "Real-time recommendations", 
                    "Advanced analytics",
                    "Microservices architecture"
                ]
            )
        }
        
        # Set V1 as deprecated with sunset date
        self.versions[APIVersion.V1].deprecated = True
        self.versions[APIVersion.V1].deprecation_date = datetime(2024, 8, 1)
        self.versions[APIVersion.V1].sunset_date = datetime(2025, 1, 1)
    
    def get_version_from_path(self, path: str) -> Optional[APIVersion]:
        """Extract API version from request path"""
        version_match = re.search(r'/api/(v\d+)/', path)
        if version_match:
            version_str = version_match.group(1)
            try:
                return APIVersion(version_str)
            except ValueError:
                return None
        return None
    
    def get_version_from_header(self, version_header: Optional[str]) -> Optional[APIVersion]:
        """Extract API version from Accept header"""
        if not version_header:
            return None
        
        # Support formats like:
        # application/vnd.aifashion.v2+json
        # application/json; version=v2
        version_match = re.search(r'v(\d+)', version_header)
        if version_match:
            version_str = f"v{version_match.group(1)}"
            try:
                return APIVersion(version_str)
            except ValueError:
                return None
        return None
    
    def get_default_version(self) -> APIVersion:
        """Get the default API version (latest non-deprecated)"""
        # Return the latest version that's not deprecated
        non_deprecated = [v for v in self.versions.values() if not v.deprecated]
        if non_deprecated:
            latest = max(non_deprecated, key=lambda v: v.release_date)
            return APIVersion(latest.version)
        return APIVersion.V2  # Fallback
    
    def validate_version(self, version: APIVersion) -> Dict[str, Any]:
        """
        Validate API version and return status information
        
        Args:
            version: API version to validate
            
        Returns:
            Dictionary with validation results and warnings
        """
        if version not in self.versions:
            return {
                "valid": False,
                "error": f"Unsupported API version: {version}",
                "supported_versions": [v.value for v in APIVersion]
            }
        
        version_info = self.versions[version]
        result = {"valid": True, "warnings": []}
        
        # Check if deprecated
        if version_info.deprecated:
            warning = f"API version {version} is deprecated"
            if version_info.sunset_date:
                warning += f" and will be removed on {version_info.sunset_date.strftime('%Y-%m-%d')}"
            result["warnings"].append(warning)
        
        # Check if sunset date is approaching
        if version_info.sunset_date and version_info.sunset_date > datetime.utcnow():
            days_until_sunset = (version_info.sunset_date - datetime.utcnow()).days
            if days_until_sunset <= 90:  # Warn if less than 90 days
                result["warnings"].append(f"API version {version} will be discontinued in {days_until_sunset} days")
        
        return result

# Global versioning manager
versioning_manager = APIVersioningManager()

def get_api_version(request: Request, accept_version: Optional[str] = Header(None)) -> APIVersion:
    """
    Determine API version from request
    
    Args:
        request: FastAPI request object
        accept_version: Optional version from Accept header
        
    Returns:
        Determined API version
    """
    # Priority order:
    # 1. Version in URL path
    # 2. Version in Accept header  
    # 3. Default version
    
    # Check URL path first
    version = versioning_manager.get_version_from_path(str(request.url.path))
    if version:
        return version
    
    # Check Accept header
    version = versioning_manager.get_version_from_header(accept_version)
    if version:
        return version
    
    # Return default version
    return versioning_manager.get_default_version()

def validate_api_version(version: APIVersion) -> None:
    """
    Validate API version and raise exception if invalid
    
    Args:
        version: API version to validate
        
    Raises:
        HTTPException: If version is invalid or sunset
    """
    validation = versioning_manager.validate_version(version)
    
    if not validation["valid"]:
        raise HTTPException(
            status_code=400,
            detail={
                "error": validation["error"],
                "supported_versions": validation.get("supported_versions", [])
            }
        )
    
    # Check if version is sunset (no longer supported)
    version_info = versioning_manager.versions[version]
    if version_info.sunset_date and version_info.sunset_date <= datetime.utcnow():
        raise HTTPException(
            status_code=410,  # Gone
            detail={
                "error": f"API version {version} is no longer supported",
                "sunset_date": version_info.sunset_date.isoformat(),
                "supported_versions": [v.value for v in APIVersion if not versioning_manager.versions[v].deprecated]
            }
        )

def add_version_headers(version: APIVersion) -> Dict[str, str]:
    """
    Generate version-related headers for response
    
    Args:
        version: Current API version
        
    Returns:
        Dictionary of headers to add to response
    """
    headers = {
        "API-Version": version.value,
        "API-Supported-Versions": ",".join([v.value for v in APIVersion])
    }
    
    # Add deprecation warnings
    validation = versioning_manager.validate_version(version)
    if validation.get("warnings"):
        headers["API-Deprecation-Warning"] = "; ".join(validation["warnings"])
    
    return headers

class VersionedAPIRouter(APIRouter):
    """
    Custom APIRouter that handles versioning
    """
    
    def __init__(self, version: APIVersion, *args, **kwargs):
        self.version = version
        # Add version prefix to all routes
        prefix = kwargs.get("prefix", "")
        kwargs["prefix"] = f"/api/{version.value}{prefix}"
        super().__init__(*args, **kwargs)
    
    def add_api_route(self, *args, **kwargs):
        # Wrap the endpoint to add version validation
        original_endpoint = kwargs.get("endpoint")
        if original_endpoint:
            def versioned_endpoint(*endpoint_args, **endpoint_kwargs):
                # Validate version
                validate_api_version(self.version)
                
                # Call original endpoint
                result = original_endpoint(*endpoint_args, **endpoint_kwargs)
                
                return result
            
            kwargs["endpoint"] = versioned_endpoint
        
        return super().add_api_route(*args, **kwargs)

def create_versioned_router(version: APIVersion, **router_kwargs) -> VersionedAPIRouter:
    """
    Create a versioned API router
    
    Args:
        version: API version for this router
        **router_kwargs: Additional arguments for APIRouter
        
    Returns:
        Configured VersionedAPIRouter
    """
    return VersionedAPIRouter(version=version, **router_kwargs)

# Middleware for adding version headers
class VersionHeadersMiddleware:
    """Middleware to add version headers to all responses"""
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extract version from request
        request = Request(scope, receive)
        try:
            version = get_api_version(request)
            headers = add_version_headers(version)
        except Exception:
            # Fallback if version detection fails
            version = versioning_manager.get_default_version()
            headers = add_version_headers(version)
        
        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                # Add version headers
                message["headers"] = list(message.get("headers", []))
                for key, value in headers.items():
                    message["headers"].append([key.encode(), value.encode()])
            
            await send(message)
        
        await self.app(scope, receive, send_with_headers)

# Version-specific response models
class BaseVersionedResponse:
    """Base class for versioned responses"""
    pass

class V1Response(BaseVersionedResponse):
    """Version 1 response format"""
    def __init__(self, data: Any):
        self.data = data
    
    def format(self) -> Dict[str, Any]:
        """Format data for v1 response"""
        return {
            "status": "success",
            "data": self.data
        }

class V2Response(BaseVersionedResponse):
    """Version 2 response format"""
    def __init__(self, data: Any, metadata: Optional[Dict] = None):
        self.data = data
        self.metadata = metadata or {}
    
    def format(self) -> Dict[str, Any]:
        """Format data for v2 response"""
        response = {
            "success": True,
            "data": self.data,
            "metadata": {
                "timestamp": datetime.utcnow().isoformat(),
                "version": "v2",
                **self.metadata
            }
        }
        return response

def format_response_for_version(data: Any, version: APIVersion, metadata: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Format response data according to API version
    
    Args:
        data: Response data
        version: API version
        metadata: Optional metadata
        
    Returns:
        Formatted response dictionary
    """
    if version == APIVersion.V1:
        return V1Response(data).format()
    elif version == APIVersion.V2:
        return V2Response(data, metadata).format()
    else:
        # Default to V2 format for unknown versions
        return V2Response(data, metadata).format()

# Version compatibility helpers
def ensure_backward_compatibility(data: Dict[str, Any], from_version: APIVersion, to_version: APIVersion) -> Dict[str, Any]:
    """
    Ensure backward compatibility when converting between API versions
    
    Args:
        data: Response data
        from_version: Source API version
        to_version: Target API version
        
    Returns:
        Compatible response data
    """
    if from_version == to_version:
        return data
    
    # V2 to V1 compatibility
    if from_version == APIVersion.V2 and to_version == APIVersion.V1:
        # Remove v2-specific fields
        if isinstance(data, dict):
            v1_data = data.copy()
            v1_data.pop("metadata", None)
            v1_data.pop("success", None)
            return {"status": "success", "data": v1_data.get("data", v1_data)}
    
    # V1 to V2 compatibility
    if from_version == APIVersion.V1 and to_version == APIVersion.V2:
        # Add v2-specific fields
        if isinstance(data, dict) and "status" in data:
            return {
                "success": data.get("status") == "success",
                "data": data.get("data", data),
                "metadata": {
                    "timestamp": datetime.utcnow().isoformat(),
                    "version": "v2",
                    "migrated_from": "v1"
                }
            }
    
    return data
