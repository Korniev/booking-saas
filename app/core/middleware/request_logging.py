import json
import time
import uuid
import traceback
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


SENSITIVE_HEADERS = {"authorization"}
SENSITIVE_FIELDS = {"password", "access_token", "refresh_token"}


def _safe_headers(headers: dict) -> dict:
    result = {}
    for k, v in headers.items():
        if k.lower() in SENSITIVE_HEADERS:
            result[k] = "***"
        else:
            result[k] = v
    return result


def _safe_json_body(body: str) -> str:
    try:
        data = json.loads(body)

        if isinstance(data, dict):
            for key in list(data.keys()):
                if key.lower() in SENSITIVE_FIELDS:
                    data[key] = "***"
        return json.dumps(data)

    except Exception:
        return body[:2000]


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable):
        request_id = str(uuid.uuid4())
        start = time.perf_counter()

        body_text = ""
        try:
            raw_body = await request.body()
            body_text = raw_body.decode("utf-8", errors="ignore")
        except Exception:
            body_text = "<unable to read body>"

        async def receive():
            return {"type": "http.request", "body": raw_body}

        request._receive = receive

        response: Response | None = None
        exc_text = None
        tb_text = None

        try:
            response = await call_next(request)
            return response

        except Exception as exc:
            exc_text = str(exc)
            tb_text = traceback.format_exc()
            raise

        finally:
            end = time.perf_counter()
            duration_ms = round((end - start) * 1000, 2)

            log_data = {
                "topic": "http_request",
                "request_id": request_id,
                "duration_ms": duration_ms,
                "request": {
                    "method": request.method,
                    "path": request.url.path,
                    "query": dict(request.query_params),
                    "headers": _safe_headers(dict(request.headers)),
                    "body": _safe_json_body(body_text),
                },
                "response": {
                    "status_code": response.status_code if response else 500,
                    "exception": exc_text,
                    "traceback": tb_text,
                },
            }

            print(json.dumps(log_data, ensure_ascii=False))

            if response:
                response.headers["X-Request-ID"] = request_id