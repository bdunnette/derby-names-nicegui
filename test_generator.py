"""Tests for the DerbyNameGenerator."""

from unittest.mock import Mock
from generator import get_generator


def test_get_generator_singleton():
    """Test that get_generator() returns the same instance."""
    # Reset the global generator
    import generator

    original_gen = generator._generator
    generator._generator = None

    try:
        gen1 = get_generator()
        gen2 = get_generator()

        assert gen1 is gen2
    finally:
        # Restore original
        generator._generator = original_gen


def test_generate_returns_string():
    """Test that generate() returns a string."""
    gen = get_generator()
    name = gen.generate()

    assert isinstance(name, str)
    assert len(name) > 0


def test_generate_with_max_attempts():
    """Test generate() with custom max_attempts."""
    gen = get_generator()
    name = gen.generate(max_attempts=10)

    assert isinstance(name, str)
    assert len(name) > 0


def test_generate_fallback_to_random_name():
    """Test that generate falls back to random name if generation fails."""
    gen = get_generator()

    # Mock both models to always return None
    original_word = gen.word_model.make_sentence
    original_char = gen.char_model.make_sentence

    try:
        gen.word_model.make_sentence = Mock(return_value=None)
        gen.char_model.make_sentence = Mock(return_value=None)

        name = gen.generate(max_attempts=1)

        # Should fall back to a random name from the training data
        assert isinstance(name, str)
        assert len(name) > 0
    finally:
        # Restore original methods
        gen.word_model.make_sentence = original_word
        gen.char_model.make_sentence = original_char


def test_generator_has_models():
    """Test that generator has both word and character models."""
    gen = get_generator()

    assert gen.word_model is not None
    assert gen.char_model is not None


def test_generator_has_names_text():
    """Test that generator loaded names text."""
    gen = get_generator()

    assert hasattr(gen, "names_text")
    assert len(gen.names_text) > 0
