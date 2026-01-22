"""
Property-based tests for input validation
Feature: music-generation-gui, Property 25: Input Parameter Validation
Validates: Requirements 5.2
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from services.validator import InputValidator

validator = InputValidator()


class TestInputValidation:
    """Unit tests for input validation"""

    def test_valid_parameters(self):
        """Test validation with valid parameters"""
        result = validator.validate({
            'seed': 'X:1',
            'temperature': 1.0,
            'length': 250
        })
        assert result['valid'] is True
        assert result['data']['seed'] == 'X:1'
        assert result['data']['temperature'] == 1.0
        assert result['data']['length'] == 250

    def test_empty_seed_uses_default(self):
        """Test that empty seed uses default"""
        result = validator.validate({
            'seed': '',
            'temperature': 1.0,
            'length': 250
        })
        assert result['valid'] is True
        assert result['data']['seed'] == validator.DEFAULT_SEED

    def test_missing_seed_uses_default(self):
        """Test that missing seed uses default"""
        result = validator.validate({
            'temperature': 1.0,
            'length': 250
        })
        assert result['valid'] is True
        assert result['data']['seed'] == validator.DEFAULT_SEED

    def test_seed_too_long(self):
        """Test that seed exceeding max length is rejected"""
        result = validator.validate({
            'seed': 'x' * 51,
            'temperature': 1.0,
            'length': 250
        })
        assert result['valid'] is False
        assert any('Seed must be at most' in error for error in result['errors'])

    def test_temperature_too_low(self):
        """Test that temperature below minimum is rejected"""
        result = validator.validate({
            'seed': 'X:1',
            'temperature': 0.05,
            'length': 250
        })
        assert result['valid'] is False
        assert any('Temperature must be between' in error for error in result['errors'])

    def test_temperature_too_high(self):
        """Test that temperature above maximum is rejected"""
        result = validator.validate({
            'seed': 'X:1',
            'temperature': 2.5,
            'length': 250
        })
        assert result['valid'] is False
        assert any('Temperature must be between' in error for error in result['errors'])

    def test_length_too_short(self):
        """Test that length below minimum is rejected"""
        result = validator.validate({
            'seed': 'X:1',
            'temperature': 1.0,
            'length': 40
        })
        assert result['valid'] is False
        assert any('Length must be between' in error for error in result['errors'])

    def test_length_too_long(self):
        """Test that length above maximum is rejected"""
        result = validator.validate({
            'seed': 'X:1',
            'temperature': 1.0,
            'length': 600
        })
        assert result['valid'] is False
        assert any('Length must be between' in error for error in result['errors'])

    def test_length_not_multiple_of_step(self):
        """Test that length not multiple of 10 is rejected"""
        result = validator.validate({
            'seed': 'X:1',
            'temperature': 1.0,
            'length': 255
        })
        assert result['valid'] is False
        assert any('Length must be a multiple of' in error for error in result['errors'])

    def test_missing_temperature(self):
        """Test that missing temperature is rejected"""
        result = validator.validate({
            'seed': 'X:1',
            'length': 250
        })
        assert result['valid'] is False
        assert any('Temperature is required' in error for error in result['errors'])

    def test_missing_length(self):
        """Test that missing length is rejected"""
        result = validator.validate({
            'seed': 'X:1',
            'temperature': 1.0
        })
        assert result['valid'] is False
        assert any('Length is required' in error for error in result['errors'])

    def test_temperature_rounding(self):
        """Test that temperature is rounded to nearest 0.1"""
        result = validator.validate({
            'seed': 'X:1',
            'temperature': 1.05,
            'length': 250
        })
        assert result['valid'] is True
        # 1.05 rounds to 1.0 (nearest 0.1)
        assert result['data']['temperature'] == 1.0


class TestInputValidationProperties:
    """Property-based tests for input validation"""

    @given(
        seed=st.text(max_size=50),
        temperature=st.floats(min_value=0.1, max_value=2.0),
        length=st.integers(min_value=50, max_value=500).filter(lambda x: x % 10 == 0)
    )
    @settings(suppress_health_check=[HealthCheck.too_slow], max_examples=50)
    def test_valid_parameters_always_pass(self, seed, temperature, length):
        """
        Property 25: Input Parameter Validation
        For any valid parameters within range, validation SHALL pass
        """
        result = validator.validate({
            'seed': seed,
            'temperature': temperature,
            'length': length
        })
        assert result['valid'] is True
        assert 'data' in result
        assert result['data']['temperature'] is not None
        assert result['data']['length'] is not None

    @given(
        seed=st.text(min_size=51, max_size=100)
    )
    def test_long_seed_always_fails(self, seed):
        """For any seed exceeding max length, validation SHALL fail"""
        result = validator.validate({
            'seed': seed,
            'temperature': 1.0,
            'length': 250
        })
        assert result['valid'] is False

    @given(
        temperature=st.floats(max_value=0.09)
    )
    def test_low_temperature_always_fails(self, temperature):
        """For any temperature below minimum, validation SHALL fail"""
        result = validator.validate({
            'seed': 'X:1',
            'temperature': temperature,
            'length': 250
        })
        assert result['valid'] is False

    @given(
        temperature=st.floats(min_value=2.01)
    )
    def test_high_temperature_always_fails(self, temperature):
        """For any temperature above maximum, validation SHALL fail"""
        result = validator.validate({
            'seed': 'X:1',
            'temperature': temperature,
            'length': 250
        })
        assert result['valid'] is False

    @given(
        length=st.integers(max_value=49)
    )
    def test_short_length_always_fails(self, length):
        """For any length below minimum, validation SHALL fail"""
        result = validator.validate({
            'seed': 'X:1',
            'temperature': 1.0,
            'length': length
        })
        assert result['valid'] is False

    @given(
        length=st.integers(min_value=501)
    )
    def test_long_length_always_fails(self, length):
        """For any length above maximum, validation SHALL fail"""
        result = validator.validate({
            'seed': 'X:1',
            'temperature': 1.0,
            'length': length
        })
        assert result['valid'] is False

    @given(
        length=st.integers(min_value=50, max_value=500).filter(lambda x: x % 10 != 0)
    )
    def test_non_step_length_always_fails(self, length):
        """For any length not multiple of 10, validation SHALL fail"""
        result = validator.validate({
            'seed': 'X:1',
            'temperature': 1.0,
            'length': length
        })
        assert result['valid'] is False
