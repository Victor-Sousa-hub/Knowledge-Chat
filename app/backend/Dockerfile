FROM python:3.11-slim

# Install uv and AWS CLI
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt-get update && apt-get install -y --no-install-recommends awscli && rm -rf /var/lib/apt/lists/*

WORKDIR /app/backend

# Copy dependency files first (layer caching)
COPY pyproject.toml uv.lock ./

# Install dependencies without dev extras
RUN uv sync --frozen --no-cache --no-dev

# Copy the full source preserving structure
COPY main.py ./
COPY src/ ./src/
COPY entrypoint.sh ./

RUN chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
CMD ["uv", "run", "uvicorn", "src.presentation.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
