# Quick Start Guide

Get EduAdvise API up and running in 5 minutes!

## Prerequisites

- Python 3.10+
- MongoDB 4.4+ (local or remote)

## Option 1: Quick Start (Development)

### 1. Clone and Setup

```bash
cd eduadvise_api
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=eduadvise
JWT_SECRET=your-secret-key-min-32-characters-long
```

### 3. Run

```bash
python run.py
```

🎉 API is now running at http://localhost:8000

Visit http://localhost:8000/docs for interactive API documentation!

## Option 2: Docker (Recommended)

### 1. Start with Docker Compose

```bash
docker-compose up -d
```

That's it! MongoDB and API are both running.

- API: http://localhost:8000
- MongoDB: localhost:27017

### 2. View Logs

```bash
docker-compose logs -f api
```

### 3. Stop

```bash
docker-compose down
```

## First API Call

### Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123456",
    "full_name": "Test User",
    "user_type": "student"
  }'
```

Response:
```json
{
  "token": "eyJ0eXAiOiJKV1Qi...",
  "user": {
    "user_id": "user_abc123",
    "email": "test@example.com",
    "full_name": "Test User",
    "user_type": "student"
  }
}
```

### Use the Token

```bash
# Save the token
TOKEN="eyJ0eXAiOiJKV1Qi..."

# Get your profile
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

## Next Steps

1. **Explore API**: Visit http://localhost:8000/docs
2. **Read Documentation**: Check out README.md
3. **Test Endpoints**: Try the API_REFERENCE.md examples
4. **Build Frontend**: Connect your frontend application

## Common Issues

### MongoDB Connection Failed

**Problem**: Can't connect to MongoDB

**Solutions**:
- **Local MongoDB**: Make sure MongoDB is running
  ```bash
  # Start MongoDB
  sudo systemctl start mongod
  # or
  brew services start mongodb-community
  ```
- **Remote MongoDB**: Check your MONGO_URL in `.env`
- **Docker**: Use `docker-compose up -d`

### Port Already in Use

**Problem**: Port 8000 is already in use

**Solution**: Change port in run command
```bash
uvicorn app.main:app --port 8001
```

### Import Errors

**Problem**: Module not found errors

**Solution**: Activate virtual environment and reinstall
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Development Tips

### Auto-reload

The server auto-reloads when you change code:
```bash
python run.py  # reload is enabled by default
```

### View Logs

```bash
# Application logs go to stdout
python run.py

# Or with more detail
LOG_LEVEL=DEBUG python run.py
```

### Interactive API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly from the browser!

## Testing the API

### Quick Test Script

```python
import requests

BASE_URL = "http://localhost:8000/api"

# Register
response = requests.post(f"{BASE_URL}/auth/register", json={
    "email": "test@example.com",
    "password": "test123456",
    "full_name": "Test User",
    "user_type": "student"
})

token = response.json()["token"]
print(f"Token: {token}")

# Get profile
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
print(f"User: {response.json()}")
```

### Run Tests

```bash
pytest
```

## Production Deployment

See DEPLOYMENT.md for production deployment guides.

## Support

- 📚 Full documentation: README.md
- 🔧 API reference: API_REFERENCE.md
- 🚀 Deployment guide: DEPLOYMENT.md
- 📝 Migration guide: MIGRATION_GUIDE.md

Happy coding! 🎉
