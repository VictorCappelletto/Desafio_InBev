"""
Load Use Cases - Data Loading Logic

Application-level logic for loading brewery data.
"""

from typing import List
from domain import Brewery
from interfaces import IDataLoader
from utils import get_logger


class LoadBreweriesUseCase:
    """
    Load breweries into destination.

    Use Case: Persist brewery entities to database/file/API.

    Responsibilities:
    - Convert entities to persistence format
    - Orchestrate loading
    - Handle errors
    - Log loading metrics
    - Return success count

    Example:
        >>> from services import AzureSQLLoader
        >>> loader = AzureSQLLoader(config)
        >>> use_case = LoadBreweriesUseCase(loader)
        >>> count = use_case.execute(breweries)
        >>> print(f"Loaded {count} breweries")
    """

    def __init__(self, loader: IDataLoader):
        """
        Initialize use case.

        Args:
            loader: Data loader implementation (DIP: depends on interface)
        """
        self.loader = loader
        self.logger = get_logger(__name__)

    def execute(self, breweries: List[Brewery]) -> int:
        """
        Execute load use case.

        Args:
            breweries: List of Brewery entities to load

        Returns:
            Number of successfully loaded records

        Raises:
            LoadError: If loading fails

        Example:
            >>> count = use_case.execute(breweries)
        """
        if not breweries:
            self.logger.warning("No breweries to load")
            return 0

        self.logger.info(f"Starting load of {len(breweries)} breweries")

        # Convert entities to dictionaries for loading
        data_to_load = [brewery.to_dict() for brewery in breweries]

        # Ensure table exists
        self.loader.create_table_if_not_exists()

        # Load data (Dependency Inversion)
        loaded_count = self.loader.load(data_to_load)

        success_rate = (loaded_count / len(breweries) * 100) if breweries else 0

        self.logger.info(
            f"Load complete: {loaded_count}/{len(breweries)} "
            f"({success_rate:.1f}% success rate)"
        )

        return loaded_count

    def execute_with_validation(
        self, breweries: List[Brewery], min_quality_score: float = 0.5
    ) -> int:
        """
        Execute load with quality validation.

        Only loads breweries that meet minimum quality threshold.

        Args:
            breweries: List of Brewery entities
            min_quality_score: Minimum quality score (0.0 to 1.0)

        Returns:
            Number of successfully loaded records

        Example:
            >>> # Only load high-quality breweries
            >>> count = use_case.execute_with_validation(
            ...     breweries,
            ...     min_quality_score=0.8
            ... )
        """
        from domain import BreweryAggregate

        self.logger.info(
            f"Validating {len(breweries)} breweries "
            f"(min_quality={min_quality_score})"
        )

        # Filter by quality
        valid_breweries = []
        rejected_count = 0

        for brewery in breweries:
            aggregate = BreweryAggregate(brewery)
            quality_score = aggregate.get_quality_score()

            if quality_score >= min_quality_score:
                valid_breweries.append(brewery)
            else:
                rejected_count += 1
                self.logger.debug(
                    f"Rejected brewery '{brewery.name}' "
                    f"(quality={quality_score:.2f})"
                )

        self.logger.info(
            f"Validation complete: {len(valid_breweries)} valid, "
            f"{rejected_count} rejected"
        )

        # Load valid breweries
        return self.execute(valid_breweries)
