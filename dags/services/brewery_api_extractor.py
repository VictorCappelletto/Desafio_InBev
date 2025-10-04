"""
Brewery API Extractor Service

Concrete implementation of IDataExtractor for Open Brewery API.
Follows Single Responsibility Principle: Only handles API extraction.
"""

from typing import Any, Dict, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from interfaces.data_extractor import IDataExtractor
from config.settings import APIConfig
from exceptions import ExtractionError, ValidationError
from utils.logger import get_logger


class BreweryAPIExtractor(IDataExtractor):
    """
    Extracts brewery data from Open Brewery DB API.
    
    This class demonstrates:
    - Single Responsibility: Only handles API extraction
    - Dependency Injection: Receives config as constructor parameter
    - Open/Closed: Can extend behavior without modifying class
    - Liskov Substitution: Can replace any IDataExtractor
    """
    
    def __init__(self, config: APIConfig):
        """
        Initialize extractor with configuration.
        
        Args:
            config: API configuration (dependency injection)
        """
        self.config = config
        self.logger = get_logger(__name__)
        self._session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        Create requests session with retry logic.
        
        Returns:
            Configured session with retry strategy
        """
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.retry_attempts,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def extract(self, **kwargs: Any) -> List[Dict[str, Any]]:
        """
        Extract brewery data from API.
        
        Supports optional parameters for pagination and filtering:
        - per_page: Number of breweries per page (default: all)
        - page: Page number for pagination (default: 1)
        - by_city: Filter by city name
        - by_state: Filter by state
        - by_type: Filter by brewery type
        
        Args:
            **kwargs: Optional query parameters for API filtering/pagination
        
        Returns:
            List of brewery dictionaries
            
        Raises:
            ExtractionError: If API call fails
            
        Example:
            >>> extractor = BreweryAPIExtractor(config)
            >>> # Get all breweries
            >>> data = extractor.extract()
            >>> # Get with pagination
            >>> data = extractor.extract(per_page=50, page=2)
            >>> # Filter by city
            >>> data = extractor.extract(by_city="San Diego")
        """
        # Build URL with query parameters
        url = self.config.brewery_api_url
        params = {k: v for k, v in kwargs.items() if v is not None}
        
        self.logger.info(
            f"Extracting data from {url}"
            + (f" with params: {params}" if params else "")
        )
        
        try:
            response = self._session.get(
                url,
                params=params,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            if not self.validate_data(data):
                raise ValidationError(
                    "API response validation failed",
                    details={"url": url, "params": params}
                )
            
            self.logger.info(f"Successfully extracted {len(data)} records")
            return data
            
        except requests.exceptions.RequestException as e:
            raise ExtractionError(
                f"Failed to extract data from API: {str(e)}",
                details={
                    "url": url,
                    "params": params,
                    "error_type": type(e).__name__
                }
            )
    
    def validate_data(self, data: List[Dict[str, Any]]) -> bool:
        """
        Validate extracted data structure.
        
        Args:
            data: Data to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not isinstance(data, list):
            self.logger.error("Data is not a list")
            return False
        
        if len(data) == 0:
            self.logger.warning("No data extracted from API")
            return True  # Empty is valid
        
        # Check first record has required fields
        required_fields = ['id', 'name', 'brewery_type']
        first_record = data[0]
        
        for field in required_fields:
            if field not in first_record:
                self.logger.error(f"Missing required field: {field}")
                return False
        
        return True
    
    def __repr__(self) -> str:
        return f"BreweryAPIExtractor(url='{self.config.brewery_api_url}')"

