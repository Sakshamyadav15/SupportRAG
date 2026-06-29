"""
Health API Tests

Tests for system health endpoints.
"""

import pytest


class TestHealthCheck:
    """Tests for GET /health"""
    
    def test_health_check(self, client):
        """Test health check returns healthy status."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data
        assert "timestamp" in data
    
    def test_health_check_no_auth_required(self, client):
        """Test health check doesn't require authentication."""
        # No auth headers provided
        response = client.get("/health")
        
        assert response.status_code == 200
