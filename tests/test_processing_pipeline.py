import pytest

from src.algorithms.processing_pipeline import ProcessingPipeline
# from src.algorithms.extractor.extractor_WFDB import WFDBExtractor
from src.algorithms.preprocessor.preprocessor_default import DefaultPreprocessor
from src.algorithms.detector.detector_default import DefaultDetector


@pytest.fixture
def pipeline():
    config = {'extractor': {'fs': 360}}
    p = ProcessingPipeline(config=config)
    return p

# --- default keys ---
def test_default_keys(pipeline):
    assert pipeline.default_modules['extractor'] == 'WFDBExtractor'
    assert pipeline.default_modules['preprocessor'] == 'DefaultPreprocessor'
    assert pipeline.default_modules['detector'] == 'DefaultDetector'

# --- get_available_modules ---
class TestGetAvailableModules:
    def test_default_extractor_present(self, pipeline):
        assert 'WFDBExtractor' in pipeline.avail_extractors

    def test_default_preprocessor_present(self, pipeline):
        assert 'DefaultPreprocessor' in pipeline.avail_preprocessors

    def test_default_detector_present(self, pipeline):
        assert 'DefaultDetector' in pipeline.avail_detectors

    def test_base_class_excluded(self, pipeline):
        assert 'BaseExtractor' not in pipeline.avail_extractors
        assert 'BasePreprocessor' not in pipeline.avail_preprocessors
        assert 'BaseDetector' not in pipeline.avail_detectors

# --- assign_module ---
class TestAssignModule:
    # figure out how to deal with WFDBExtractor's set_config here first
    # def test_default_extractor_assigned(self, pipeline):
    #     pipeline.assign_module('extractor', pipeline.avail_extractors)
    #     assert isinstance(pipeline.extractor, WFDBExtractor)

    def test_default_preprocessor_assigned(self, pipeline):
        pipeline.assign_module('preprocessor', pipeline.avail_preprocessors)
        assert isinstance(pipeline.preprocessor, DefaultPreprocessor)

    def test_default_detector_assigned(self, pipeline):
        pipeline.assign_module('detector', pipeline.avail_detectors)
        assert isinstance(pipeline.detector, DefaultDetector)

    def test_fallback_on_invalid_module_name(self, pipeline):
        pipeline.config_global = {'detector': {'active': 'NonExistentModule'}}
        pipeline.assign_module('detector', pipeline.avail_detectors)
        assert isinstance(pipeline.detector, DefaultDetector)
