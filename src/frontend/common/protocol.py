"""Frontend-backend communication protocol.

All communication between frontends and backend uses
structured Request/Response objects.
"""

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class Request:
    """A request from frontend to backend.

    Attributes:
        method: The backend method to call.
        params: Parameters for the method.
        request_id: Optional unique request identifier.
    """

    method: str
    params: dict[str, Any] = field(default_factory=dict)
    request_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "method": self.method,
            "params": self.params,
            "request_id": self.request_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Request":
        """Create from dictionary."""
        return cls(
            method=data["method"],
            params=data.get("params", {}),
            request_id=data.get("request_id"),
        )


@dataclass
class Response:
    """A response from backend to frontend.

    Attributes:
        success: Whether the request succeeded.
        data: Response data.
        error: Error message if failed.
        request_id: Matching request identifier.
    """

    success: bool
    data: Any = None
    error: Optional[str] = None
    request_id: Optional[str] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "request_id": self.request_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Response":
        """Create from dictionary."""
        return cls(
            success=data["success"],
            data=data.get("data"),
            error=data.get("error"),
            request_id=data.get("request_id"),
        )


class ServiceProtocol:
    """Protocol for frontend-backend communication.

    Provides a registry of callable backend functions
    that frontends can discover and invoke.
    """

    def __init__(self) -> None:
        """Initialize the protocol."""
        self._handlers: dict[str, Any] = {}
        self._descriptions: dict[str, str] = {}

    def register(
        self,
        method: str,
        handler: Any,
        description: str = "",
    ) -> None:
        """Register a backend method handler.

        Args:
            method: Method name.
            handler: Callable handler.
            description: Method description.
        """
        self._handlers[method] = handler
        self._descriptions[method] = description

    def unregister(self, method: str) -> None:
        """Unregister a method.

        Args:
            method: Method name.
        """
        self._handlers.pop(method, None)
        self._descriptions.pop(method, None)

    def handle(self, request: Request) -> Response:
        """Handle a frontend request.

        Args:
            request: The request to handle.

        Returns:
            Response with result or error.
        """
        handler = self._handlers.get(request.method)
        if not handler:
            return Response(
                success=False,
                error=f"Unknown method: {request.method}",
                request_id=request.request_id,
            )
        try:
            result = handler(**request.params)
            return Response(
                success=True,
                data=result,
                request_id=request.request_id,
            )
        except Exception as e:
            return Response(
                success=False,
                error=str(e),
                request_id=request.request_id,
            )

    def get_methods(self) -> list[dict[str, str]]:
        """Get all registered methods and descriptions.

        Returns:
            List of method info dictionaries.
        """
        return [
            {"method": name, "description": desc}
            for name, desc in self._descriptions.items()
        ]
