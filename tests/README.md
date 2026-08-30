# SANTINEL Framework Test Suite

Complete pytest suite for testing all 10 integrated psychology frameworks and the Unified Coach orchestration layer.

## Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt  # Includes pytest and pytest-cov
```

### Run All Tests
```bash
pytest tests/ -v
```

### Run with Coverage Report
```bash
pytest tests/ --cov=core --cov-report=term-missing --cov-report=html
```

## Test Organization

### Test Files

| File | Tests | Focus |
|------|-------|-------|
| `test_frameworks.py` | 78 | All 10 core frameworks + integration |
| `test_feedback_extraction.py` | 34 | Verbal/vocal signals + close probability |
| `test_sales_scripts.py` | 31 | Script selection + personality matching |
| `test_unified_coach.py` | 22 | Multi-framework orchestration |

### Total Coverage: 165 Tests

## Running Specific Tests

### By Framework
```bash
# Test one framework
pytest tests/test_frameworks.py::TestTAFramework -v

# Test TA ego state detection specifically
pytest tests/test_frameworks.py::TestTAFramework::test_ego_state_detection_en -v
```

### By Test Type (Markers)
```bash
# Unit tests only
pytest tests/ -m unit

# Integration tests only
pytest tests/ -m integration

# Bilingual tests (EN + RO)
pytest tests/ -m bilingual

# Edge case tests
pytest tests/ -m edge_case

# All except slow tests
pytest tests/ -m "not slow"
```

### By Test Class
```bash
# All feedback extraction tests
pytest tests/test_feedback_extraction.py::TestFeedbackExtractionFramework -v

# All sales scripts tests
pytest tests/test_sales_scripts.py::TestSalesScriptsFramework -v

# All unified coach tests
pytest tests/test_unified_coach.py::TestUnifiedCoachFramework -v
```

## Test Categories

### Unit Tests (78 tests)
Individual framework tests validating:
- Signal detection accuracy
- Pattern matching
- Scoring algorithms
- Keyword matching (EN + RO)

**Run:**
```bash
pytest tests/ -m unit -v
```

### Integration Tests (52 tests)
Multi-framework tests validating:
- Framework interaction
- Data flow between frameworks
- Unified coach orchestration
- Conflict detection
- Synergy identification

**Run:**
```bash
pytest tests/ -m integration -v
```

### Bilingual Tests (22 tests)
English and Romanian language support:
- Signal detection in both languages
- Mixed language handling
- Keyword matching accuracy
- Regional variations

**Run:**
```bash
pytest tests/ -m bilingual -v
```

### Edge Case Tests (18 tests)
Robustness validation:
- Empty text handling
- Very long text (1000+ words)
- Special characters (!@#$%^&*)
- Unicode characters (😊✨)
- Repeated patterns
- Rapid sequential calls

**Run:**
```bash
pytest tests/ -m edge_case -v
```

## Test Fixtures

Common fixtures available in `conftest.py`:

### Framework Instances
```python
def test_something(ta_module, ei_module, unified_coach):
    # All 10 frameworks available as fixtures
    result = ta_module.detect_ego_state("I love this idea!")
    assert result is not None
```

### Sample Test Data
```python
def test_with_samples(sample_texts_en, sample_texts_ro):
    text = sample_texts_en["agreement"]
    # Texts for: agreement, objection, doubt, stalling, question, urgency, budget, competitive
```

### Negotiation Scenarios
```python
def test_scenarios(negotiation_scenarios_en):
    for scenario in negotiation_scenarios_en:
        name = scenario["name"]
        text = scenario["text"]
        patterns = scenario["expected_patterns"]
```

## Coverage Reports

### Terminal Output
```bash
pytest tests/ --cov=core --cov-report=term-missing
```

Shows:
- Line coverage for each module
- Missing lines not covered by tests
- Overall coverage percentage

### HTML Report
```bash
pytest tests/ --cov=core --cov-report=html
open coverage_html/index.html  # or start coverage_html/index.html on Windows
```

Interactive HTML report with:
- Line-by-line coverage highlighting
- Branch coverage
- Coverage trends
- Drill-down to specific files

## Test Output Options

### Verbose Output
```bash
pytest tests/ -v  # Show each test
```

### Extra Summary
```bash
pytest tests/ -ra  # Show all test summary info
```

### Stop on First Failure
```bash
pytest tests/ -x  # Stop immediately
pytest tests/ --maxfail=3  # Stop after 3 failures
```

### Show Print Statements
```bash
pytest tests/ -s  # Show stdout/print output
```

### Parallel Execution
```bash
pytest tests/ -n auto  # Requires pytest-xdist
```

## Test Structure Example

```python
class TestTAFramework:
    """Tests for TA (Transactional Analysis) framework."""

    @pytest.mark.unit
    def test_ego_state_detection_en(self, ta_module, sample_texts_en):
        """Test ego state detection in English."""
        result = ta_module.detect_ego_state(sample_texts_en["agreement"])
        assert result is not None
        assert "ego_state" in result or "primary_ego_state" in result

    @pytest.mark.bilingual
    def test_ego_state_detection_ro(self, ta_module, sample_texts_ro):
        """Test ego state detection in Romanian."""
        result = ta_module.detect_ego_state(sample_texts_ro["agreement"])
        assert result is not None

    @pytest.mark.edge_case
    def test_empty_text_ta(self, ta_module):
        """Test TA framework with empty text."""
        result = ta_module.detect_ego_state("")
        assert result is not None
```

## Common Test Patterns

### Testing Framework Detection
```python
def test_framework_detects_pattern(self, framework_module):
    text = "some negotiation text"
    result = framework_module.analyze(text)
    assert result is not None
    assert "expected_key" in result
```

### Testing Dual-Speaker Analysis
```python
def test_dual_speaker_comparison(self, framework_module):
    your_text = "I believe this is great"
    their_text = "I'm not sure about this"
    result = framework_module.dual_speaker_analysis(your_text, their_text)
    assert result is not None
```

### Testing Scoring
```python
def test_scoring_range(self, framework_module):
    result = framework_module.score_something("text")
    assert 0 <= result["score"] <= 1
```

## Troubleshooting

### Import Errors
```
ModuleNotFoundError: No module named 'core'
```
**Solution:** Ensure you're running from the repo root, or pytest is in the path.

### Test Collection Errors
```
ERROR collecting tests/test_framework.py
```
**Solution:** Check for syntax errors in test files, ensure fixtures are imported.

### Fixture Not Found
```
fixture 'ta_module' not found
```
**Solution:** Ensure `conftest.py` is in the `tests/` directory.

## Continuous Integration

For GitHub Actions or similar:

```yaml
- name: Run tests
  run: |
    pip install -r requirements.txt
    pytest tests/ --cov=core --cov-report=xml --junitxml=test-results.xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Performance Notes

- Full test suite: ~90 seconds
- Unit tests only: ~45 seconds
- Single test: ~0.5 seconds

To run tests faster:
```bash
pytest tests/ -n auto  # Parallel execution (requires pytest-xdist)
pytest tests/ -m "not slow"  # Skip slow tests
```

## Adding New Tests

1. Create test file: `tests/test_new_framework.py`
2. Import fixtures from conftest: `def test_something(framework_module)`
3. Add markers: `@pytest.mark.unit`, `@pytest.mark.bilingual`, etc.
4. Run: `pytest tests/test_new_framework.py -v`

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/fixture.html)
- [Pytest Markers](https://docs.pytest.org/en/stable/how-to-use-pytest-mark-by-name.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)

## Test Results Summary

Current status:
- ✅ **134 passing** (81.2%)
- ❌ **31 failing** (18.8%) - mostly API structure differences
- ⚠️ Expected adjustments needed for close probability calibration

See `TESTING_REPORT.md` for detailed analysis.
