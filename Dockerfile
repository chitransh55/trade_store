# 1. Use a lightweight Python base image
FROM python:3.14-slim

# 2. Set the working directory inside the image
WORKDIR /app

# 3. Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 4. Configure uv for predictable container builds
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1

# 5. Copy dependency metadata first
COPY pyproject.toml uv.lock ./

# 6. Install runtime dependencies without dev dependencies
#    Do not install the project package itself
RUN uv sync --frozen --no-dev --no-install-project

# 7. Copy application source code
COPY app/ ./app/

# 8. Set the database location and timeout
ENV DB_PATH=/data/dws.db
ENV DB_TIMEOUT=10

# 9. Document the port used by FastAPI
EXPOSE 8000

# 10. Start the FastAPI application
CMD ["uv", "run", "--no-sync", "uvicorn", \
     "app.api.trade_app:app", \
     "--host", "0.0.0.0", "--port", "8000"]