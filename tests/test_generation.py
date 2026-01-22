"""
Property-based tests for generation API
Feature: music-generation-gui, Property 24: Backend Generation Functionality
Feature: music-generation-gui, Property 26: Invalid Parameter Error Response
Validates: Requirements 5.1, 5.3
"""
import pytest
import json
from hypothesis import given, strategies as st, settings, HealthCheck
from app import app
from services.validator import InputValidator

validator = InputValidator()


@pytest.fixture(scope='session')
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestGenerationAPI:
    """Unit tests for generation API"""

    def test_generate_with_valid_parameters(self, client):
        """Test generation with valid parameters"""
        response = client.post('/api/generate', json={
            'seed': 'X:1',
            'temperature': 1.0,
            'length': 250
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'notation' in data
        assert 'timestamp' in data
        assert 'parameters' in data
        assert isinstance(data['notation'], str)

    def test_generate_with_empty_seed(self, client):
        """Test generation with empty seed uses default"""
        response = client.post('/api/generate', json={
            'seed': '',
            'temperature': 1.0,
            'length': 250
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'notation' in data

    def test_generate_with_missing_seed(self, client):
        """Test generation with missing seed uses default"""
        response = client.post('/api/generate', json={
            'temperature': 1.0,
            'length': 250
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'notation' in data

    def test_generate_with_invalid_temperature(self, client):
        """Test generation with invalid temperature returns 400"""
        response = client.post('/api/generate', json={
            'seed': 'X:1',
            'temperature': 0.05,
            'length': 250
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_generate_with_invalid_length(self, client):
        """Test generation with invalid length returns 400"""
        response = client.post('/api/generate', json={
            'seed': 'X:1',
            'temperature': 1.0,
            'length': 40
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_generate_with_missing_temperature(self, client):
        """Test generation with missing temperature returns 400"""
        response = client.post('/api/generate', json={
            'seed': 'X:1',
            'length': 250
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_generate_with_missing_length(self, client):
        """Test generation with missing length returns 400"""
        response = client.post('/api/generate', json={
            'seed': 'X:1',
            'temperature': 1.0
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/api/health')
        assert response.status_code == 200
        data = response.get_json()
        assert 'status' in data
        assert 'model_loaded' in data


class TestGenerationAPIProperties:
    """Property-based tests for generation API"""

    @given(
        seed=st.text(max_size=50),
        temperature=st.floats(min_value=0.1, max_value=2.0),
        length=st.integers(min_value=50, max_value=500).filter(lambda x: x % 10 == 0)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture], max_examples=20, deadline=3000)
    def test_valid_generation_returns_200(self, client, seed, temperature, length):
        """
        Property 24: Backend Generation Functionality
        For any valid generation request, backend SHALL return 200 with notation
        """
        response = client.post('/api/generate', json={
            'seed': seed,
            'temperature': temperature,
            'length': length
        })
        assert response.status_code == 200
        data = response.get_json()
        assert 'notation' in data
        assert isinstance(data['notation'], str)
        assert len(data['notation']) > 0
        assert 'timestamp' in data
        assert 'parameters' in data

    @given(
        seed=st.text(min_size=51, max_size=100)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture], max_examples=20)
    def test_long_seed_returns_400(self, client, seed):
        """
        Property 26: Invalid Parameter Error Response
        For any request with invalid seed, backend SHALL return 400
        """
        response = client.post('/api/generate', json={
            'seed': seed,
            'temperature': 1.0,
            'length': 250
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    @given(
        temperature=st.floats(max_value=0.09)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture], max_examples=20)
    def test_low_temperature_returns_400(self, client, temperature):
        """For any request with temperature below minimum, backend SHALL return 400"""
        response = client.post('/api/generate', json={
            'seed': 'X:1',
            'temperature': temperature,
            'length': 250
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    @given(
        temperature=st.floats(min_value=2.01)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture], max_examples=20)
    def test_high_temperature_returns_400(self, client, temperature):
        """For any request with temperature above maximum, backend SHALL return 400"""
        response = client.post('/api/generate', json={
            'seed': 'X:1',
            'temperature': temperature,
            'length': 250
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    @given(
        length=st.integers(max_value=49)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture], max_examples=20)
    def test_short_length_returns_400(self, client, length):
        """For any request with length below minimum, backend SHALL return 400"""
        response = client.post('/api/generate', json={
            'seed': 'X:1',
            'temperature': 1.0,
            'length': length
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    @given(
        length=st.integers(min_value=501)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture], max_examples=20)
    def test_long_length_returns_400(self, client, length):
        """For any request with length above maximum, backend SHALL return 400"""
        response = client.post('/api/generate', json={
            'seed': 'X:1',
            'temperature': 1.0,
            'length': length
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
