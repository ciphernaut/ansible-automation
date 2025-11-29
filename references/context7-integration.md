# Context7 Integration Details

## Overview

The ansible-automation skill leverages Context7 for real-time access to current Ansible documentation, best practices, and community patterns. This integration ensures that all automation follows the latest standards and avoids outdated practices.

## Integration Points

### 1. Script-Level Integration

All helper scripts automatically integrate Context7 when available:

```python
# Standard Context7 integration pattern
try:
    from context7 import get_ansible_docs, get_best_practices
    context7_available = True
except ImportError:
    context7_available = False

def get_module_docs(module_name):
    """Get current module documentation from Context7"""
    if context7_available:
        return get_ansible_docs(module_name, tokens=3000)
    return fallback_module_docs(module_name)
```

### 2. Automatic Best Practice Updates

Context7 provides:
- **Current Module Documentation**: Latest parameter changes and deprecation warnings
- **Security Best Practices**: Up-to-date security configurations and patterns
- **Performance Patterns**: Current optimization techniques and benchmarks
- **Community Standards**: Latest community-approved automation patterns

### 3. Smart Query System

Context7 integration uses intelligent querying:

```python
def get_context7_help(query, context_type="general"):
    """Get targeted Context7 assistance"""
    if context_type == "module":
        return get_ansible_docs(query, tokens=2000)
    elif context_type == "best_practices":
        return get_best_practices(query, tokens=1500)
    elif context_type == "troubleshooting":
        return get_ansible_docs(query, topic="troubleshooting", tokens=2500)
```

## Usage Patterns

### Playbook Generation
```bash
# Generate with Context7 best practices
python3 scripts/generate_playbook.py --template webserver --context7-enabled

# Get current module examples
python3 scripts/generate_playbook.py --module nginx --context7-examples
```

### Community Module Management
```bash
# Search with current documentation
python3 scripts/community_manager.py search nginx --context7-docs

# Get installation best practices
python3 scripts/community_manager.py install community.mongodb --context7-guidance
```

### Deployment Assistance
```bash
# Deployment with current best practices
python3 scripts/deploy_helper.py deploy.yml inventory.yml --context7-optimization

# Troubleshooting with current solutions
python3 scripts/deploy_helper.py --troubleshoot "service failing" --context7-help
```

## Context7 Features

### 1. Real-Time Documentation
- **Module Parameters**: Current parameter lists and usage patterns
- **Deprecation Warnings**: Automatic alerts for deprecated features
- **New Features**: Information about newly added capabilities
- **Version Compatibility**: Cross-version compatibility information

### 2. Best Practice Engine
- **Security Patterns**: Current security best practices and configurations
- **Performance Optimization**: Latest performance tuning techniques
- **Compliance Standards**: Updated compliance requirements and patterns
- **Community Standards**: Current community-approved approaches

### 3. Pattern Recognition
- **Reusable Patterns**: Identifies and suggests reusable automation patterns
- **Anti-Pattern Detection**: Warns about common anti-patterns and pitfalls
- **Template Generation**: Creates templates based on current best practices
- **Workflow Optimization**: Suggests workflow improvements

### 4. Troubleshooting Assistance
- **Current Solutions**: Latest troubleshooting approaches and solutions
- **Common Issues**: Updated lists of common issues and fixes
- **Debugging Techniques**: Current debugging methodologies and tools
- **Performance Issues**: Latest performance problem diagnosis

## Configuration

### Environment Variables
```bash
# Enable/disable Context7 integration
ANSIBLE_CONTEXT7_ENABLED=true

# Context7 API configuration
CONTEXT7_API_KEY=your_api_key
CONTEXT7_ENDPOINT=https://api.context7.com

# Query optimization
CONTEXT7_DEFAULT_TOKENS=3000
CONTEXT7_CACHE_TTL=3600
```

### Script Configuration
```python
# context7_config.py
CONTEXT7_SETTINGS = {
    'enabled': True,
    'default_tokens': 3000,
    'cache_ttl': 3600,
    'fallback_enabled': True,
    'query_timeout': 30,
    'retry_attempts': 3
}
```

## Fallback Behavior

When Context7 is unavailable, scripts gracefully fallback to:

1. **Cached Documentation**: Previously retrieved and cached information
2. **Static Examples**: Built-in examples and patterns
3. **Generic Best Practices**: Standard Ansible best practices
4. **Offline Mode**: Continue operation with reduced functionality

## Performance Optimization

### Caching Strategy
```python
# Intelligent caching for Context7 responses
@lru_cache(maxsize=128)
def get_cached_context7_docs(query, tokens=3000):
    """Cache Context7 responses for performance"""
    if context7_available:
        return get_ansible_docs(query, tokens=tokens)
    return None
```

### Query Optimization
- **Token Management**: Optimize token usage for cost efficiency
- **Batch Queries**: Combine related queries when possible
- **Selective Usage**: Use Context7 only for complex or critical operations
- **Background Updates**: Update documentation in background processes

## Error Handling

### Graceful Degradation
```python
def safe_context7_call(func, *args, **kwargs):
    """Safely call Context7 with fallback"""
    try:
        if context7_available:
            return func(*args, **kwargs)
    except Exception as e:
        logger.warning(f"Context7 unavailable: {e}")
    return fallback_response(*args, **kwargs)
```

### Error Recovery
- **Automatic Retry**: Retry failed Context7 calls with exponential backoff
- **Fallback Activation**: Automatically switch to cached or static content
- **Error Logging**: Log Context7 errors for troubleshooting
- **User Notification**: Inform users when Context7 is unavailable

## Best Practices

### 1. Efficient Usage
- Use Context7 for complex or critical operations only
- Cache responses to avoid repeated queries
- Optimize token usage for cost efficiency
- Use specific, targeted queries

### 2. Fallback Planning
- Always provide fallback mechanisms
- Maintain offline functionality
- Cache frequently used documentation
- Test fallback scenarios regularly

### 3. Performance Considerations
- Monitor Context7 response times
- Optimize query patterns
- Use background updates for non-critical data
- Implement intelligent caching strategies

### 4. Security
- Protect Context7 API keys
- Validate Context7 responses
- Monitor for unusual query patterns
- Implement rate limiting where appropriate

## Troubleshooting

### Common Issues
1. **Context7 Unavailable**: Scripts automatically fallback to cached content
2. **Slow Responses**: Check network connectivity and API limits
3. **Outdated Cache**: Clear cache and refresh documentation
4. **API Key Issues**: Verify Context7 API configuration

### Debug Commands
```bash
# Test Context7 connectivity
python3 scripts/generate_playbook.py --test-context7

# Clear Context7 cache
python3 scripts/generate_playbook.py --clear-cache

# Check Context7 status
python3 scripts/community_manager.py --context7-status
```