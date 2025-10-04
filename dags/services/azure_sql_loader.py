"""
Azure SQL Loader Service

Concrete implementation of IDataLoader for Azure SQL Database.
Follows Single Responsibility Principle: Only handles SQL loading.
"""

from typing import Any, Dict, List

import pyodbc
from config.settings import AzureSQLConfig
from exceptions import LoadError
from interfaces.data_loader import IDataLoader
from utils.logger import get_logger


class AzureSQLLoader(IDataLoader):
    """
    Loads brewery data into Azure SQL Database.

    This class demonstrates:
    - Single Responsibility: Only handles SQL loading
    - Dependency Injection: Receives config and table_name as parameters
    - Open/Closed: Can extend without modifying
    - Proper resource management: Context managers for connections
    - Flexibility: Table name is configurable (not hardcoded)

    Example:
        >>> loader = AzureSQLLoader(config, table_name="Breweries")
        >>> loader.create_table_if_not_exists()
        >>> count = loader.load(data)
    """

    def __init__(self, config: AzureSQLConfig, table_name: str = "Breweries"):
        """
        Initialize loader with configuration.

        Args:
            config: Azure SQL configuration (dependency injection)
            table_name: Name of the target table (default: "Breweries")
        """
        self.config = config
        self.table_name = table_name
        self.logger = get_logger(__name__)

    def _get_connection(self) -> pyodbc.Connection:
        """
        Create database connection.

        Returns:
            Database connection

        Raises:
            LoadError: If connection fails
        """
        try:
            conn_string = self.config.connection_string
            return pyodbc.connect(conn_string)
        except pyodbc.Error as e:
            raise LoadError(
                f"Failed to connect to Azure SQL: {str(e)}",
                details={
                    "server": self.config.server,
                    "database": self.config.database,
                },
            )

    def create_table_if_not_exists(self) -> None:
        """
        Create table if it doesn't exist.

        Creates a table with brewery schema in Azure SQL Database.
        Table name is configurable via constructor.

        Raises:
            LoadError: If table creation fails
        """
        create_table_sql = f"""
        IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{self.table_name}' and xtype='U')
        CREATE TABLE {self.table_name} (
            id NVARCHAR(200) PRIMARY KEY,
            name NVARCHAR(255),
            brewery_type NVARCHAR(100),
            address_1 NVARCHAR(255),
            address_2 NVARCHAR(255),
            address_3 NVARCHAR(255),
            city NVARCHAR(100),
            state_province NVARCHAR(100),
            postal_code NVARCHAR(50),
            country NVARCHAR(100),
            longitude FLOAT,
            latitude FLOAT,
            phone NVARCHAR(50),
            website_url NVARCHAR(500),
            state NVARCHAR(100),
            street NVARCHAR(255)
        )
        """

        self.logger.info(f"Creating table {self.table_name} if not exists")

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(create_table_sql)
                conn.commit()

            self.logger.info(f"Table {self.table_name} ready")

        except pyodbc.Error as e:
            raise LoadError(
                f"Failed to create table: {str(e)}", details={"table": self.table_name}
            )

    def load(self, data: List[Dict[str, Any]], **kwargs: Any) -> int:
        """
        Load brewery data into Azure SQL.

        Uses MERGE statement for upsert behavior (insert or skip if exists).
        Processes records one by one to handle individual failures gracefully.

        Optional parameters:
        - batch_size: Number of records per transaction (not implemented yet)
        - skip_errors: Continue on individual record errors (default: True)

        Args:
            data: List of brewery dictionaries
            **kwargs: Optional loading parameters (reserved for future use)

        Returns:
            Number of records successfully loaded

        Raises:
            LoadError: If loading fails critically

        Example:
            >>> loader = AzureSQLLoader(config, table_name="Breweries")
            >>> count = loader.load(data)
            >>> print(f"Loaded {count} records")
        """
        if not data:
            self.logger.warning("No data to load")
            return 0

        self.logger.info(f"Loading {len(data)} records to {self.table_name}")

        # MERGE statement for upsert (insert only if not exists)
        insert_sql = f"""
        MERGE {self.table_name} AS target
        USING (SELECT ? AS id) AS source
        ON target.id = source.id
        WHEN NOT MATCHED THEN
            INSERT (id, name, brewery_type, address_1, address_2, address_3,
                    city, state_province, postal_code, country, longitude,
                    latitude, phone, website_url, state, street)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """

        loaded_count = 0

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()

                for brewery in data:
                    try:
                        cursor.execute(
                            insert_sql,
                            brewery.get("id"),
                            brewery.get("id"),
                            brewery.get("name"),
                            brewery.get("brewery_type"),
                            brewery.get("address_1"),
                            brewery.get("address_2"),
                            brewery.get("address_3"),
                            brewery.get("city"),
                            brewery.get("state_province"),
                            brewery.get("postal_code"),
                            brewery.get("country"),
                            brewery.get("longitude"),
                            brewery.get("latitude"),
                            brewery.get("phone"),
                            brewery.get("website_url"),
                            brewery.get("state"),
                            brewery.get("street"),
                        )
                        loaded_count += 1
                    except pyodbc.Error as e:
                        self.logger.warning(
                            f"Failed to load brewery {brewery.get('id')}: {e}"
                        )
                        # Continue with next record (skip_errors behavior)
                        continue

                conn.commit()

            self.logger.info(f"Successfully loaded {loaded_count}/{len(data)} records")
            return loaded_count

        except pyodbc.Error as e:
            raise LoadError(
                f"Failed to load data: {str(e)}",
                details={"records_attempted": len(data)},
            )

    def __repr__(self) -> str:
        return (
            f"AzureSQLLoader(server='{self.config.server}', "
            f"database='{self.config.database}', "
            f"table='{self.table_name}')"
        )
