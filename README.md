# EduAdvise - International Student Counseling Platform API

A production-ready FastAPI backend for an international student counseling platform with real-time messaging, video/audio calls, booking management, and file sharing capabilities.

## 🚀 Features

- **Authentication & Authorization**: JWT-based authentication with bcrypt password hashing
- **Real-time Messaging**: WebSocket-powered chat system with typing indicators
- **Video/Audio Calls**: WebRTC-based calling with TURN server support
- **Booking Management**: Service booking system for counseling sessions
- **File Sharing**: Secure file upload and download with validation
- **Email Notifications**: Automated email notifications (mock implementation)
- **In-app Reminders**: Reminder system for upcoming sessions
- **User Profiles**: Student and counselor profiles with extended metadata

## 📋 Prerequisites

- Python 3.10 or higher
- MongoDB 4.4 or higher
- (Optional) TURN server for production WebRTC calls

## 🛠️ Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd eduadvise_api
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
# Required
MONGO_URL=mongodb://localhost:27017
DB_NAME=eduadvise
JWT_SECRET=your-secure-secret-key-min-32-characters

# Optional
GOOGLE_CALENDAR_CLIENT_ID=your-client-id
GOOGLE_CALENDAR_CLIENT_SECRET=your-client-secret
```

### 5. Create uploads directory

```bash
mkdir -p uploads
```

## 🚀 Running the Application

### Development Mode

```bash
# Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using the main.py script
python -m app.main
```

### Production Mode

```bash
# Using uvicorn with workers
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Or using gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

The API will be available at `http://localhost:8000`

## 📚 API Documentation

Once the application is running, access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🏗️ Project Structure

```
eduadvise_api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Core functionality
│   │   ├── __init__.py
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database connection
│   │   └── security.py        # Authentication & security
│   ├── routers/               # API route handlers
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication routes
│   │   ├── messages.py       # Messaging routes
│   │   ├── calls.py          # Call management routes
│   │   └── files.py          # File upload/download
│   ├── schemas/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── messages.py
│   │   ├── bookings.py
│   │   └── calls.py
│   ├── services/             # Business logic
│   │   ├── __init__.py
│   │   ├── websocket.py      # WebSocket manager
│   │   ├── email.py          # Email service
│   │   └── reminder.py       # Reminder service
│   └── utils/                # Utility functions
│       ├── __init__.py
│       └── websocket_handler.py
├── tests/                    # Test files
├── uploads/                  # File upload directory
├── .env.example             # Environment variables template
├── .gitignore
├── requirements.txt
└── README.md
```

## 🔑 Key Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user profile
- `PUT /api/auth/me` - Update user profile
- `POST /api/auth/change-password` - Change password

### Messaging
- `POST /api/messages/send` - Send a message
- `GET /api/messages/conversations` - Get all conversations
- `GET /api/messages/conversations/{id}/messages` - Get conversation messages

### Calls
- `POST /api/calls/initiate` - Initiate a call
- `PUT /api/calls/{id}/status` - Update call status
- `POST /api/calls/{id}/signal` - Send WebRTC signaling data
- `GET /api/calls/webrtc-config` - Get TURN server configuration
- `GET /api/calls/history` - Get call history

### Files
- `POST /api/files/upload` - Upload a file
- `GET /api/files/{filename}` - Download a file

### WebSocket
- `WS /ws/{user_id}` - WebSocket connection for real-time updates

## 🔐 Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_auth.py
```

## 📝 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| MONGO_URL | MongoDB connection string | Yes | - |
| DB_NAME | MongoDB database name | Yes | - |
| JWT_SECRET | Secret key for JWT tokens | Yes | - |
| JWT_ALGORITHM | JWT algorithm | No | HS256 |
| JWT_EXPIRATION_HOURS | Token expiration time | No | 168 |
| GOOGLE_CALENDAR_CLIENT_ID | Google Calendar API client ID | No | - |
| GOOGLE_CALENDAR_CLIENT_SECRET | Google Calendar API secret | No | - |
| LOG_LEVEL | Logging level | No | INFO |

## 🔧 Configuration

### TURN Server Setup

For production video/audio calls, configure TURN servers in your `.env` or `config.py`:

```python
TURN_SERVERS = [
    {
        "urls": "stun:stun.l.google.com:19302"
    },
    {
        "urls": "turn:your-turn-server.com:3478",
        "username": "user",
        "credential": "pass"
    }
]
```

### MongoDB Indexes

For optimal performance, create these indexes:

```javascript
// Users
db.users.createIndex({ "email": 1 }, { unique: true })
db.users.createIndex({ "user_id": 1 }, { unique: true })

// Messages
db.messages.createIndex({ "conversation_id": 1, "created_at": -1 })
db.messages.createIndex({ "receiver_id": 1, "is_read": 1 })

// Conversations
db.conversations.createIndex({ "participants": 1 })
db.conversations.createIndex({ "updated_at": -1 })

// Call Sessions
db.call_sessions.createIndex({ "call_id": 1 }, { unique: true })
db.call_sessions.createIndex({ "caller_id": 1, "created_at": -1 })
db.call_sessions.createIndex({ "receiver_id": 1, "created_at": -1 })
```

## 🚀 Deployment

### Using Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using Docker Compose

```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGO_URL=mongodb://mongodb:27017
      - DB_NAME=eduadvise
    depends_on:
      - mongodb
    
  mongodb:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db

volumes:
  mongodb_data:
```

## 📊 Monitoring & Logging

The application uses Python's built-in logging module. Logs are output to stdout with the following format:

```
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Configure log level via the `LOG_LEVEL` environment variable.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support, email support@eduadvise.com or create an issue in the repository.

## 🔄 Migration from emergent.sh

This codebase has been restructured from an emergent.sh generated script to follow FastAPI best practices:

### Key Improvements:
- ✅ Proper project structure with separation of concerns
- ✅ Type hints and Pydantic validation throughout
- ✅ Dependency injection for database and authentication
- ✅ Environment-based configuration
- ✅ Improved error handling and logging
- ✅ Modular router organization
- ✅ Service layer for business logic
- ✅ Production-ready with proper startup/shutdown handlers

### Breaking Changes:
None - The API endpoints remain compatible with the original implementation.
