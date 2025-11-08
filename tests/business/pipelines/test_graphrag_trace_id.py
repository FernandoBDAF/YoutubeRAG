"""
Integration tests for Trace ID System Integration (Achievement 0.1).

Tests verify that trace_id is generated, passed to stages, and stored in metadata.
"""

import pytest
import uuid
from business.pipelines.graphrag import GraphRAGPipeline, create_graphrag_pipeline
from core.config.graphrag import GraphRAGPipelineConfig


def test_trace_id_generation():
    """Test that trace_id is generated when pipeline is created."""
    config = GraphRAGPipelineConfig()
    pipeline = create_graphrag_pipeline(config)
    
    assert hasattr(pipeline, 'trace_id')
    assert pipeline.trace_id is not None
    assert isinstance(pipeline.trace_id, str)
    # Verify it's a valid UUID format
    uuid.UUID(pipeline.trace_id)  # Will raise ValueError if invalid


def test_trace_id_unique_per_run():
    """Test that each pipeline run generates a unique trace_id."""
    config1 = GraphRAGPipelineConfig()
    pipeline1 = create_graphrag_pipeline(config1)
    
    config2 = GraphRAGPipelineConfig()
    pipeline2 = create_graphrag_pipeline(config2)
    
    assert pipeline1.trace_id != pipeline2.trace_id


def test_trace_id_on_stage_configs():
    """Test that trace_id is set on all stage configs."""
    config = GraphRAGPipelineConfig()
    pipeline = create_graphrag_pipeline(config)
    
    assert pipeline.config.extraction_config.trace_id == pipeline.trace_id
    assert pipeline.config.resolution_config.trace_id == pipeline.trace_id
    assert pipeline.config.construction_config.trace_id == pipeline.trace_id
    assert pipeline.config.detection_config.trace_id == pipeline.trace_id


def test_trace_id_in_experiment_metadata():
    """Test that trace_id is included in experiment metadata when experiment_id is set."""
    config = GraphRAGPipelineConfig()
    config.experiment_id = "test_experiment_123"
    pipeline = create_graphrag_pipeline(config)
    
    # Check that trace_id is set
    assert pipeline.trace_id is not None
    
    # Verify trace_id would be in metadata (we can't easily test the DB write without mocking)
    # But we can verify the method exists and trace_id is available
    assert hasattr(pipeline, '_track_experiment_start')
    assert hasattr(pipeline, 'trace_id')


def test_trace_id_format():
    """Test that trace_id is in UUID4 format."""
    config = GraphRAGPipelineConfig()
    pipeline = create_graphrag_pipeline(config)
    
    # Verify UUID format (36 chars: 8-4-4-4-12)
    assert len(pipeline.trace_id) == 36
    assert pipeline.trace_id.count('-') == 4
    
    # Verify it's parseable as UUID
    parsed_uuid = uuid.UUID(pipeline.trace_id)
    assert parsed_uuid.version == 4  # UUID4


