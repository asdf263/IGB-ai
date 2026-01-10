# Development Guide

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   Create a `.env` file:
   ```
   GEMINI_API_KEY=your_api_key_here
   PORT=5000
   ```

3. **Run the Server**
   ```bash
   python app.py
   ```

## Project Structure

```
backend/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── tests/              # Test files
│   └── test_app.py
└── docs/               # Documentation
    ├── API_DOCUMENTATION.md
    ├── CHATBOT_GUIDE.md
    └── DEVELOPMENT_GUIDE.md
```

## Testing

Run tests:
```bash
python -m unittest discover tests
```

Or with pytest:
```bash
pytest tests/
```

## Code Style

- Follow PEP 8 style guide
- Use type hints where appropriate
- Add docstrings to functions and classes
- Keep functions focused and single-purpose

## Adding New Features

1. Create feature branch
2. Implement feature with tests
3. Update documentation
4. Submit for review

## Debugging

Enable debug mode in `app.py`:
```python
app.run(debug=True)
```

Check logs for detailed error messages.

## Deployment

1. Set production environment variables
2. Use a production WSGI server (e.g., Gunicorn)
3. Configure reverse proxy (e.g., Nginx)
4. Set up SSL/TLS certificates
5. Configure CORS for production domain

