"""
Tests for serialization library converters.

Run with: python -m tests.core.libraries.serialization.test_converters
"""

from datetime import datetime
from decimal import Decimal
from bson import ObjectId, Decimal128
from pydantic import BaseModel

from core.libraries.serialization import to_dict, from_dict, json_encoder
from core.models.graphrag import EntityModel, RelationshipModel, EntityType


def test_to_dict_simple_model():
    """Test converting simple Pydantic model to dict."""

    class SimpleModel(BaseModel):
        name: str
        age: int

    model = SimpleModel(name="John", age=30)
    result = to_dict(model)

    assert result == {"name": "John", "age": 30}
    assert isinstance(result, dict)
    print("✓ to_dict with simple model")


def test_from_dict_simple_model():
    """Test creating Pydantic model from dict."""

    class SimpleModel(BaseModel):
        name: str
        age: int

    data = {"name": "Jane", "age": 25}
    model = from_dict(SimpleModel, data)

    assert isinstance(model, SimpleModel)
    assert model.name == "Jane"
    assert model.age == 25
    print("✓ from_dict with simple model")


def test_roundtrip_entity_model():
    """Test roundtrip conversion of EntityModel."""
    # Create entity
    entity = EntityModel(
        name="Python",
        type=EntityType.TECHNOLOGY,
        description="Programming language",
        confidence=0.95,
    )

    # Convert to dict
    entity_dict = to_dict(entity)
    assert entity_dict["name"] == "Python"
    assert entity_dict["type"] == "TECHNOLOGY"
    assert entity_dict["confidence"] == 0.95

    # Convert back
    entity_restored = from_dict(EntityModel, entity_dict)
    assert entity_restored.name == entity.name
    assert entity_restored.type == entity.type
    assert entity_restored.confidence == entity.confidence
    print("✓ Roundtrip with EntityModel")


def test_roundtrip_relationship_model():
    """Test roundtrip conversion of RelationshipModel."""
    source = EntityModel(
        name="Python",
        type=EntityType.TECHNOLOGY,
        description="Programming language",
        confidence=0.9,
    )
    target = EntityModel(
        name="Django",
        type=EntityType.TECHNOLOGY,
        description="Web framework for Python",
        confidence=0.9,
    )

    rel = RelationshipModel(
        source_entity=source,
        target_entity=target,
        relation="uses",
        description="Python uses Django",
        confidence=0.85,
    )

    # Convert to dict
    rel_dict = to_dict(rel)
    assert rel_dict["relation"] == "uses"
    assert rel_dict["source_entity"]["name"] == "Python"

    # Convert back
    rel_restored = from_dict(RelationshipModel, rel_dict)
    assert rel_restored.relation == rel.relation
    assert rel_restored.source_entity.name == source.name
    print("✓ Roundtrip with RelationshipModel")


def test_encode_object_id():
    """Test encoding ObjectId to string."""
    obj_id = ObjectId()
    result = json_encoder(obj_id)
    assert isinstance(result, str)
    assert len(result) == 24  # ObjectId string length
    print("✓ JSON encode ObjectId")


def test_encode_datetime():
    """Test encoding datetime to ISO string."""
    dt = datetime(2025, 11, 3, 12, 30, 45)
    result = json_encoder(dt)
    assert isinstance(result, str)
    assert "2025-11-03" in result
    assert "12:30:45" in result
    print("✓ JSON encode datetime")


def test_encode_decimal128():
    """Test encoding Decimal128 to float."""
    dec = Decimal128(Decimal("123.45"))
    result = json_encoder(dec)
    assert isinstance(result, float)
    assert abs(result - 123.45) < 0.01
    print("✓ JSON encode Decimal128")


def test_encode_regular_types():
    """Test that regular types pass through."""
    assert json_encoder(42) == 42
    assert json_encoder("test") == "test"
    assert json_encoder([1, 2, 3]) == [1, 2, 3]
    assert json_encoder({"key": "value"}) == {"key": "value"}
    print("✓ JSON encode regular types")


def test_encode_mixed_dict():
    """Test encoding dict with MongoDB types."""
    data = {
        "id": ObjectId(),
        "timestamp": datetime(2025, 11, 3),
        "amount": Decimal128(Decimal("99.99")),
        "name": "test",
        "count": 5,
    }

    # Process each value through encoder
    result = {k: json_encoder(v) for k, v in data.items()}

    assert isinstance(result["id"], str)
    assert isinstance(result["timestamp"], str)
    assert isinstance(result["amount"], float)
    assert result["name"] == "test"
    assert result["count"] == 5
    print("✓ JSON encode mixed dict")


def test_to_dict_with_none():
    """Test to_dict with None value."""
    result = to_dict(None)
    assert result is None
    print("✓ to_dict with None")


def test_from_dict_with_extra_fields():
    """Test from_dict ignores extra fields."""

    class StrictModel(BaseModel):
        name: str

    data = {"name": "test", "extra": "ignored"}
    model = from_dict(StrictModel, data)
    assert model.name == "test"
    assert not hasattr(model, "extra")
    print("✓ from_dict ignores extra fields")


def test_from_dict_with_missing_optional():
    """Test from_dict with missing optional field."""

    class OptionalModel(BaseModel):
        name: str
        optional: str = "default"

    data = {"name": "test"}
    model = from_dict(OptionalModel, data)
    assert model.name == "test"
    assert model.optional == "default"
    print("✓ from_dict with missing optional field")


def run_all_tests():
    """Run all tests."""
    print("=== Testing Serialization Library ===\n")

    test_to_dict_simple_model()
    test_from_dict_simple_model()
    test_roundtrip_entity_model()
    test_roundtrip_relationship_model()
    test_encode_object_id()
    test_encode_datetime()
    test_encode_decimal128()
    test_encode_regular_types()
    test_encode_mixed_dict()
    test_to_dict_with_none()
    test_from_dict_with_extra_fields()
    test_from_dict_with_missing_optional()

    print("\n✅ All serialization tests passed!")


if __name__ == "__main__":
    run_all_tests()
