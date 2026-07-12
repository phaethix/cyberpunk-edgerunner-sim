# Read the doc: https://huggingface.co/docs/hub/spaces-sdks-docker
# you will also find guides on how best to write your Dockerfile

FROM python:3.12-slim

RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

ENV PYTHONPATH="/app"
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install dependencies first (better layer caching) from the slimmed prod file.
COPY --chown=user requirements-prod.txt requirements.txt
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY --chown=user . /app

# Single worker keeps memory footprint minimal for the free CPU tier.
EXPOSE 7860
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
