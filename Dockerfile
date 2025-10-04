FROM quay.io/astronomer/astro-runtime:13.2.0

# ==============================================================================
# Microsoft ODBC Driver 18 - COMMENTED OUT (apt-key deprecated in Docker)
# ==============================================================================
# Install locally via Astro CLI if needed for SQL Server connections
# For production, use managed identity or connection strings
#
# USER root
# RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
#     && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
#     && apt-get update \
#     && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/*
# USER astro
#
# Note: For portfolio/demo, SQL connections can use SQLAlchemy with other drivers
# ==============================================================================

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
