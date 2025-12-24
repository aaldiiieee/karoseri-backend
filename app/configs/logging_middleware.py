import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware untuk logging semua request dan response."""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        # Get User-Agent
        user_agent = request.headers.get("user-agent", "unknown")
        user_agent_short = user_agent.split("/")[0].split(" ")[0]
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request - format langsung di message
        logging.info(
            f"[{request_id}] Request: {request.method} {request.url.path} "
            f"| IP: {client_ip} | User-Agent: {user_agent_short}"
        )
        
        try:
            response = await call_next(request)
            duration = time.time() - start_time
            
            # Log response
            logging.info(
                f"[{request_id}] Response: {response.status_code} "
                f"| Duration: {duration:.3f}s \n"
            )
            
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            duration = time.time() - start_time
            logging.error(
                f"[{request_id}] Error: {str(e)} | Duration: {duration:.3f}s"
            )
            raise