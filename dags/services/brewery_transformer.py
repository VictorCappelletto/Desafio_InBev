"""
Brewery Transformer Service

Concrete implementation of IDataTransformer for brewery data.
Follows Single Responsibility Principle: Only handles data transformation.
"""

from typing import Any, Dict, List

from interfaces.data_transformer import IDataTransformer
from exceptions import TransformationError
from utils.logger import get_logger


class BreweryTransformer(IDataTransformer):
    """
    Transforms brewery data for Azure SQL loading.
    
    This class demonstrates:
    - Single Responsibility: Only handles transformation logic
    - Open/Closed: Can add new transformation rules without changing core logic
    """
    
    def __init__(self):
        """Initialize transformer."""
        self.logger = get_logger(__name__)
    
    def transform(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform brewery data.
        
        Transformations applied:
        - Normalize None values
        - Truncate long strings
        - Validate data types
        
        Args:
            data: Raw brewery data
            
        Returns:
            Transformed brewery data
            
        Raises:
            TransformationError: If transformation fails
        """
        if not data:
            return []
        
        self.logger.info(f"Transforming {len(data)} records")
        
        try:
            transformed_data = [
                self._transform_record(record)
                for record in data
            ]
            
            self.logger.info(f"Successfully transformed {len(transformed_data)} records")
            return transformed_data
            
        except Exception as e:
            raise TransformationError(
                f"Failed to transform data: {str(e)}"
            )
    
    def _transform_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a single brewery record.
        
        Args:
            record: Single brewery dictionary
            
        Returns:
            Transformed record
        """
        return {
            'id': self._safe_string(record.get('id'), max_length=200),
            'name': self._safe_string(record.get('name'), max_length=255),
            'brewery_type': self._safe_string(record.get('brewery_type'), max_length=100),
            'address_1': self._safe_string(record.get('address_1'), max_length=255),
            'address_2': self._safe_string(record.get('address_2'), max_length=255),
            'address_3': self._safe_string(record.get('address_3'), max_length=255),
            'city': self._safe_string(record.get('city'), max_length=100),
            'state_province': self._safe_string(record.get('state_province'), max_length=100),
            'postal_code': self._safe_string(record.get('postal_code'), max_length=50),
            'country': self._safe_string(record.get('country'), max_length=100),
            'longitude': self._safe_float(record.get('longitude')),
            'latitude': self._safe_float(record.get('latitude')),
            'phone': self._safe_string(record.get('phone'), max_length=50),
            'website_url': self._safe_string(record.get('website_url'), max_length=500),
            'state': self._safe_string(record.get('state'), max_length=100),
            'street': self._safe_string(record.get('street'), max_length=255),
        }
    
    @staticmethod
    def _safe_string(value: Any, max_length: int = None) -> str:
        """
        Safely convert value to string.
        
        Args:
            value: Value to convert
            max_length: Maximum string length
            
        Returns:
            String value or None
        """
        if value is None:
            return None
        
        str_value = str(value)
        
        if max_length and len(str_value) > max_length:
            return str_value[:max_length]
        
        return str_value
    
    @staticmethod
    def _safe_float(value: Any) -> float:
        """
        Safely convert value to float.
        
        Args:
            value: Value to convert
            
        Returns:
            Float value or None
        """
        if value is None:
            return None
        
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def __repr__(self) -> str:
        return "BreweryTransformer()"

