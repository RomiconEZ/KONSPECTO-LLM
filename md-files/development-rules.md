# Development Guidelines for KONSPECTO

## 1. Code Organization

### Backend Structure
- FastAPI application structure with clear separation of concerns
- Use of dependency injection and service pattern
- Modular organization with agent tools and services

### Frontend Structure
- React components with proper separation
- Context-based state management
- Consistent styling with TailwindCSS

## 2. Technology Stack

### Backend
- Python 3.11
- FastAPI
- LangChain for agent implementation
- Redis Stack for storage
- Whisper for voice transcription
- OpenCV and Pillow for image processing

### Frontend
- React 18.2.0
- Vite
- TailwindCSS
- React Router
- React Icons

## 3. Development Standards

### Python Code Style
```python
# Example of proper Python code style
class SearchTool:
    """
    Tool for performing search operations using query_engine.
    """
    @staticmethod
    def search(query: str) -> List[str]:
        """
        Performs document search for given text query.

        Args:
            query: Text query for searching documents.
        Returns:
            List of search result texts.
        """
```

### JavaScript Code Style
```javascript
// Example of proper React component style
const GoogleDocViewer = React.memo(({ fileId, onClose }) => {
  if (!fileId) return null;

  return (
    <div className="flex flex-col h-full w-full relative">
      {/* Component content */}
    </div>
  );
});
```

## 4. Testing Requirements

### Backend Tests
- Use pytest for testing
- Maintain high test coverage
- Mock external services
- Test both success and error cases

### Frontend Tests
- Use Jest and React Testing Library
- Test component rendering
- Test user interactions
- Test API integration

## 5. Documentation Requirements

### Code Documentation
- Clear and concise docstrings
- Type hints for Python code
- PropTypes for React components
- Comments for complex logic

### API Documentation
- OpenAPI/Swagger documentation
- Clear endpoint descriptions
- Request/response examples

## 6. Version Control

### Branches
- main: Production code
- develop: Development code
- feature/*: New features
- fix/*: Bug fixes

### Commit Messages
```
feat: Add video processing functionality
fix: Resolve chat context persistence
docs: Update API documentation
style: Format code according to standards
```

## 7. Build and Deployment

### Docker
- Use multi-stage builds
- Optimize image sizes
- Proper environment variable handling

### CI/CD
- Run tests before merging
- Automated builds
- Code quality checks

## 8. Security

### General Rules
- No hardcoded credentials
- Proper error handling
- Input validation
- Secure file handling

### Environment Variables
- Use .env files
- Separate configs for different environments
- Never commit sensitive data

## 9. Performance

### Backend
- Async operations where possible
- Proper error handling
- Cache when appropriate

### Frontend
- Lazy loading
- Memoization
- Optimized re-renders

## 10. Tools and Utilities

### Development Tools
- Poetry for Python dependency management
- npm for JavaScript dependency management
- pre-commit hooks
- ESLint and Prettier

### Monitoring and Logging
- Structured logging
- Error tracking
- Performance monitoring