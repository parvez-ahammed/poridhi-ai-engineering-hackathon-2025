FROM python:3.10-slim AS builder

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY ./apps/search_api/requirements-app.txt .
RUN /opt/venv/bin/pip install pip --upgrade && \
    /opt/venv/bin/pip install -r requirements-app.txt --no-cache-dir

COPY ./apps/search_api/requirements-mon.txt .
RUN /opt/venv/bin/pip install pip --upgrade && \
    /opt/venv/bin/pip install -r requirements-mon.txt --no-cache-dir

FROM python:3.10-slim AS runner
WORKDIR /opt/webapp
RUN groupadd -g 1001 fastapi \
    && useradd -u 1001 -g fastapi -m -d /opt/webapp fastapi \
    && chown fastapi:fastapi -R /opt/webapp
USER fastapi

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY --chown=fastapi:fastapi ./apps/search_api /opt/webapp


CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
