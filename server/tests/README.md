# CIP Server Tests

Comprehensive test suite for the CIP Server.

## Running Tests

### All Tests
```bash
pytest
```

### Specific Test File
```bash
pytest tests/test_parsers.py
pytest tests/test_services.py
```

### Specific Test Class
```bash
pytest tests/test_parsers.py::TestPythonParser
```

### Specific Test
```bash
pytest tests/test_parsers.py::TestPythonParser::test_parse_python_code
```

### With Coverage
```bash
pytest --cov=. --cov-report=html
```

### Verbose Output
```bash
pytest -v
```

### Stop on First Failure
```bash
pytest -x
```

## Test Organization

### Unit Tests
Fast, isolated tests with mocked dependencies:
- `test_parsers.py` - Parser functionality
- `test_services.py` - Service layer logic
- `test_config.py` - Configuration management
- `test_api.py` - API endpoint routing
- `test_webhook.py` - Webhook handling

### Integration Tests
Slower tests that may use real resources:
- `test_integration.py` - End-to-end workflows

Run only unit tests:
```bash
pytest -m unit
```

Run only integration tests:
```bash
pytest -m integration
```

## Test Coverage

Current test coverage:

### Parsers (test_parsers.py)
- ✅ PythonParser: 12 tests
  - File recognition
  - Function/class/method extraction
  - Docstring parsing
  - Import detection
  - Signature extraction
  - Error handling
  
- ✅ MarkdownParser: 4 tests
  - File recognition
  - Section extraction
  - Link detection
  - Heading levels
  
- ✅ YamlParser: 5 tests
  - File recognition
  - meta.yaml parsing
  - Schema validation
  - Error handling

### Services (test_services.py)
- ✅ KnowledgeGraphService: 6 tests
  - Initialization
  - Query operations
  - Node retrieval
  - Concept tracing
  - Related node finding
  
- ✅ IndexingService: 10 tests
  - Initialization
  - Job queuing
  - Status tracking
  - Force sync
  - Repo removal
  - Queue statistics
  - Skip patterns
  - Entity type mapping
  
- ✅ ValidationService: 1 test
  - Basic initialization
  
- ✅ NavigationService: 2 tests
  - Initialization with/without repos
  
- ✅ ScoringService: 1 test
  - Basic initialization

### API Endpoints (test_api.py)
- ✅ GraphAPI: 6 tests
  - Query endpoint
  - Get node endpoint
  - Node not found handling
  - Trace concept endpoint
  - Find related endpoint
  
- ✅ IndexAPI: 5 tests
  - Index repo endpoint
  - Sync status endpoint
  - Force sync endpoint
  - Remove repo endpoint
  - Queue status endpoint
  
- ✅ Error Handling: 2 tests
  - Service unavailable scenarios

### Configuration (test_config.py)
- ✅ ServerConfig: 8 tests
  - Default configuration
  - Config from dictionary
  - Storage configuration
  - LLM configuration
  - Webhook configuration
  - YAML file loading
  - Invalid config handling
  - Missing fields handling

### Webhooks (test_webhook.py)
- ✅ WebhookHandler: 7 tests
  - GitHub signature verification
  - GitLab token verification
  - Push event handling (GitHub/GitLab)
  - Branch filtering
  
- ✅ Webhook Endpoints: 3 tests
  - GitHub endpoint
  - GitLab endpoint
  - Bitbucket endpoint

### Integration (test_integration.py)
- ✅ Indexing Integration: 2 tests
  - Index small repository
  - Skip ignored files
  
- ✅ Query Integration: 1 test
  - Query after indexing
  
- ✅ End-to-End: 1 test
  - Full workflow (index → query → get node)

## Total: 78+ Tests

## Fixtures

Available in `conftest.py`:

- `event_loop` - Async event loop for async tests
- `temp_dir` - Temporary directory for test files
- `sample_python_code` - Sample Python code for parsing
- `sample_markdown` - Sample Markdown content
- `sample_meta_yaml` - Sample meta.yaml content
- `mock_storage` - Mocked Kronos storage
- `sample_config` - Sample server configuration

## Adding New Tests

### Template for Service Tests
```python
class TestMyService:
    """Tests for MyService."""
    
    def test_initialization(self):
        """Test service initialization."""
        from services import MyService
        service = MyService()
        assert service is not None
    
    @pytest.mark.asyncio
    async def test_async_method(self, mock_storage):
        """Test async method."""
        from services import MyService
        service = MyService(mock_storage)
        result = await service.my_method()
        assert result is not None
```

### Template for API Tests
```python
def test_my_endpoint(test_app):
    """Test my endpoint."""
    client = TestClient(test_app)
    response = client.get("/api/my-endpoint")
    
    assert response.status_code == 200
    data = response.json()
    assert "key" in data
```

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run tests
  run: |
    pip install -r requirements.txt
    pip install pytest pytest-asyncio pytest-cov
    pytest --cov --cov-report=xml
```

## Troubleshooting

### Import Errors
Make sure you're running from the server directory:
```bash
cd cip-core/server
PYTHONPATH=. pytest
```

### Async Tests Failing
Ensure pytest-asyncio is installed:
```bash
pip install pytest-asyncio
```

### Mock Issues
Check that unittest.mock is available (Python 3.3+)

## Best Practices

1. **Isolate Tests**: Use mocks to avoid external dependencies
2. **Test Edge Cases**: Empty inputs, invalid data, errors
3. **Use Fixtures**: Reuse common test setup
4. **Clear Names**: Test names should describe what they test
5. **Fast Tests**: Keep unit tests fast (<100ms each)
6. **Async Aware**: Mark async tests with `@pytest.mark.asyncio`
7. **Cleanup**: Use fixtures with proper cleanup (temp files, etc.)
