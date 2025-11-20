"""Audit logging for security-relevant events."""

import logging
from datetime import datetime
from typing import Optional


# Create dedicated audit logger
audit_logger = logging.getLogger('audit')
audit_logger.setLevel(logging.INFO)


class AuditLog:
    """Centralized audit logging for security events.

    Tracks authentication attempts, authorization failures, and
    sensitive operations for security monitoring and compliance.

    Log Format: EVENT_TYPE|timestamp|user_info|details
    """

    @staticmethod
    def log_auth_attempt(username: str, success: bool, ip_address: str, details: str = "") -> None:
        """Log authentication attempt.

        Args:
            username: Username (not logged for security, only hashed)
            success: Whether authentication succeeded
            ip_address: Client IP address
            details: Additional context (error type, etc.)

        Examples:
            >>> AuditLog.log_auth_attempt("user123", True, "192.168.1.1")
            # Logs: AUTH_ATTEMPT|2025-11-12T10:30:00|success|192.168.1.1

            >>> AuditLog.log_auth_attempt("user123", False, "192.168.1.1", "invalid_password")
            # Logs: AUTH_ATTEMPT|2025-11-12T10:30:00|failure|192.168.1.1|invalid_password
        """
        status = "success" if success else "failure"
        timestamp = datetime.utcnow().isoformat()

        audit_logger.info(
            f"AUTH_ATTEMPT|{timestamp}|{status}|{ip_address}|{details}"
        )

    @staticmethod
    def log_registration(success: bool, ip_address: str, details: str = "") -> None:
        """Log user registration attempt.

        Args:
            success: Whether registration succeeded
            ip_address: Client IP address
            details: Additional context

        Examples:
            >>> AuditLog.log_registration(True, "192.168.1.1")
            # Logs: REGISTRATION|2025-11-12T10:30:00|success|192.168.1.1
        """
        status = "success" if success else "failure"
        timestamp = datetime.utcnow().isoformat()

        audit_logger.info(
            f"REGISTRATION|{timestamp}|{status}|{ip_address}|{details}"
        )

    @staticmethod
    def log_sensitive_action(
        user_id: int,
        action: str,
        resource: str,
        success: bool = True,
        details: str = ""
    ) -> None:
        """Log sensitive operations (voting, data modification, etc.).

        Args:
            user_id: User performing the action
            action: Type of action (UPVOTE, DOWNVOTE, DELETE, etc.)
            resource: Resource being acted upon (news_id, etc.)
            success: Whether operation succeeded
            details: Additional context

        Examples:
            >>> AuditLog.log_sensitive_action(123, "UPVOTE", "news_45")
            # Logs: ACTION|2025-11-12T10:30:00|user_123|UPVOTE|news_45|success
        """
        status = "success" if success else "failure"
        timestamp = datetime.utcnow().isoformat()

        audit_logger.info(
            f"ACTION|{timestamp}|user_{user_id}|{action}|{resource}|{status}|{details}"
        )

    @staticmethod
    def log_security_event(
        event_type: str,
        severity: str,
        details: str,
        ip_address: Optional[str] = None
    ) -> None:
        """Log security-relevant events (rate limiting, suspicious activity).

        Args:
            event_type: Type of security event (RATE_LIMIT, SUSPICIOUS, etc.)
            severity: Event severity (INFO, WARNING, CRITICAL)
            details: Event description
            ip_address: Optional client IP

        Examples:
            >>> AuditLog.log_security_event("RATE_LIMIT", "WARNING", "Exceeded login attempts", "192.168.1.1")
            # Logs: SECURITY|2025-11-12T10:30:00|WARNING|RATE_LIMIT|192.168.1.1|Exceeded login attempts
        """
        timestamp = datetime.utcnow().isoformat()
        ip_info = ip_address or "unknown"

        audit_logger.warning(
            f"SECURITY|{timestamp}|{severity}|{event_type}|{ip_info}|{details}"
        )

    @staticmethod
    def log_authorization_failure(
        user_id: Optional[int],
        resource: str,
        required_permission: str,
        ip_address: str
    ) -> None:
        """Log authorization failures (access denied).

        Args:
            user_id: User attempting access (None if unauthenticated)
            resource: Resource being accessed
            required_permission: Permission that was missing
            ip_address: Client IP address

        Examples:
            >>> AuditLog.log_authorization_failure(123, "/admin", "admin_role", "192.168.1.1")
            # Logs: AUTHZ_FAILURE|2025-11-12T10:30:00|user_123|/admin|admin_role|192.168.1.1
        """
        timestamp = datetime.utcnow().isoformat()
        user_info = f"user_{user_id}" if user_id else "unauthenticated"

        audit_logger.warning(
            f"AUTHZ_FAILURE|{timestamp}|{user_info}|{resource}|{required_permission}|{ip_address}"
        )
