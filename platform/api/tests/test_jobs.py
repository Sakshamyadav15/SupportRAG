"""
Jobs API Tests

Tests for job endpoints.
"""

import pytest


class TestCreateJob:
    """Tests for POST /jobs"""
    
    def test_create_job_success(self, client, auth_headers):
        """Test successful job creation."""
        response = client.post(
            "/jobs",
            json={"input_data": {"task": "test", "value": 123}},
            headers=auth_headers
        )
        
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["status"] == "COMPLETED"  # Sync processing in Phase 1
        assert data["result_data"] is not None
    
    def test_create_job_unauthorized(self, client):
        """Test job creation without auth fails."""
        response = client.post(
            "/jobs",
            json={"input_data": {"task": "test"}}
        )
        
        assert response.status_code == 401
    
    def test_create_job_invalid_token(self, client):
        """Test job creation with invalid token fails."""
        response = client.post(
            "/jobs",
            json={"input_data": {"task": "test"}},
            headers={"Authorization": "Bearer invalidtoken"}
        )
        
        assert response.status_code == 401


class TestListJobs:
    """Tests for GET /jobs"""
    
    def test_list_jobs_empty(self, client, auth_headers):
        """Test listing jobs when none exist."""
        response = client.get("/jobs", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["jobs"] == []
        assert data["total"] == 0
    
    def test_list_jobs_with_jobs(self, client, auth_headers):
        """Test listing jobs after creating some."""
        # Create jobs
        for i in range(3):
            client.post(
                "/jobs",
                json={"input_data": {"task": f"test{i}"}},
                headers=auth_headers
            )
        
        response = client.get("/jobs", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) == 3
        assert data["total"] == 3
    
    def test_list_jobs_pagination(self, client, auth_headers):
        """Test job listing pagination."""
        # Create jobs
        for i in range(5):
            client.post(
                "/jobs",
                json={"input_data": {"task": f"test{i}"}},
                headers=auth_headers
            )
        
        response = client.get("/jobs?skip=2&limit=2", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["jobs"]) == 2
        assert data["total"] == 5
    
    def test_list_jobs_unauthorized(self, client):
        """Test listing jobs without auth fails."""
        response = client.get("/jobs")
        
        assert response.status_code == 401


class TestGetJob:
    """Tests for GET /jobs/{id}"""
    
    def test_get_job_success(self, client, auth_headers):
        """Test getting a job by ID."""
        # Create a job
        create_response = client.post(
            "/jobs",
            json={"input_data": {"task": "test"}},
            headers=auth_headers
        )
        job_id = create_response.json()["id"]
        
        response = client.get(f"/jobs/{job_id}", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == job_id
    
    def test_get_job_not_found(self, client, auth_headers):
        """Test getting non-existent job returns 404."""
        response = client.get("/jobs/99999", headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_get_job_unauthorized(self, client):
        """Test getting job without auth fails."""
        response = client.get("/jobs/1")
        
        assert response.status_code == 401
    
    def test_get_job_other_user(self, client, auth_headers):
        """Test that users cannot access other users' jobs."""
        # Create a job with first user
        create_response = client.post(
            "/jobs",
            json={"input_data": {"task": "test"}},
            headers=auth_headers
        )
        job_id = create_response.json()["id"]
        
        # Register and login as second user
        client.post(
            "/auth/register",
            json={"email": "other@example.com", "password": "password123"}
        )
        login_response = client.post(
            "/auth/login",
            json={"email": "other@example.com", "password": "password123"}
        )
        other_token = login_response.json()["access_token"]
        other_headers = {"Authorization": f"Bearer {other_token}"}
        
        # Try to access first user's job
        response = client.get(f"/jobs/{job_id}", headers=other_headers)
        
        assert response.status_code == 404
