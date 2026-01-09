# API Reference

Complete API documentation for EduAdvise platform.

## Base URL

```
http://localhost:8000/api
```

## Authentication

All authenticated endpoints require a JWT token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

---

## Authentication Endpoints

### Register User

Create a new user account.

**Endpoint:** `POST /auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe",
  "user_type": "student",
  "phone": "+1234567890",
  "country": "USA",
  "timezone": "America/New_York",
  "avatar_url": "https://example.com/avatar.jpg"
}
```

**Response:** `200 OK`
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "user_id": "user_abc123",
    "email": "user@example.com",
    "full_name": "John Doe",
    "user_type": "student",
    "phone": "+1234567890",
    "country": "USA",
    "timezone": "America/New_York",
    "avatar_url": "https://example.com/avatar.jpg",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### Login

Authenticate and receive JWT token.

**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response:** `200 OK`
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "user_id": "user_abc123",
    "email": "user@example.com",
    "full_name": "John Doe",
    "user_type": "student",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### Get Current User

Get authenticated user's profile.

**Endpoint:** `GET /auth/me`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "user_id": "user_abc123",
  "email": "user@example.com",
  "full_name": "John Doe",
  "user_type": "student",
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Update Profile

Update current user's profile.

**Endpoint:** `PUT /auth/me`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "full_name": "John Updated Doe",
  "phone": "+1234567890",
  "country": "Canada"
}
```

**Response:** `200 OK` (Updated user object)

### Change Password

Change user's password.

**Endpoint:** `POST /auth/change-password`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "old_password": "oldpassword123",
  "new_password": "newpassword456"
}
```

**Response:** `200 OK`
```json
{
  "message": "Password changed successfully"
}
```

---

## Messaging Endpoints

### Send Message

Send a message to another user.

**Endpoint:** `POST /messages/send`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "receiver_id": "user_def456",
  "content": "Hello! How can I help you?",
  "file_url": "https://example.com/file.pdf",
  "file_name": "document.pdf"
}
```

**Response:** `200 OK`
```json
{
  "message_id": "msg_xyz789",
  "conversation_id": "conv_abc123",
  "sender_id": "user_abc123",
  "receiver_id": "user_def456",
  "content": "Hello! How can I help you?",
  "file_url": "https://example.com/file.pdf",
  "file_name": "document.pdf",
  "is_read": false,
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Get Conversations

Get all conversations for current user.

**Endpoint:** `GET /messages/conversations`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
[
  {
    "conversation_id": "conv_abc123",
    "participants": ["user_abc123", "user_def456"],
    "last_message": {
      "message_id": "msg_xyz789",
      "content": "Hello!",
      "created_at": "2024-01-01T12:00:00Z"
    },
    "unread_count": 2,
    "created_at": "2024-01-01T10:00:00Z",
    "updated_at": "2024-01-01T12:00:00Z"
  }
]
```

### Get Conversation Messages

Get messages from a specific conversation.

**Endpoint:** `GET /messages/conversations/{conversation_id}/messages`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `limit` (optional): Number of messages to return (default: 50)

**Response:** `200 OK`
```json
[
  {
    "message_id": "msg_xyz789",
    "conversation_id": "conv_abc123",
    "sender_id": "user_abc123",
    "receiver_id": "user_def456",
    "content": "Hello!",
    "is_read": true,
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

---

## Call Endpoints

### Initiate Call

Start a voice or video call.

**Endpoint:** `POST /calls/initiate`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "receiver_id": "user_def456",
  "call_type": "video"
}
```

**Response:** `200 OK`
```json
{
  "call_id": "call_xyz789",
  "caller_id": "user_abc123",
  "receiver_id": "user_def456",
  "call_type": "video",
  "status": "ringing",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Update Call Status

Update the status of a call (accept, decline, end).

**Endpoint:** `PUT /calls/{call_id}/status`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "status": "accepted"
}
```

**Valid status values:**
- `accepted` - Call was answered
- `declined` - Call was rejected
- `ended` - Call was terminated
- `missed` - Call was not answered

**Response:** `200 OK`
```json
{
  "call_id": "call_xyz789",
  "caller_id": "user_abc123",
  "receiver_id": "user_def456",
  "call_type": "video",
  "status": "accepted",
  "started_at": "2024-01-01T12:00:00Z",
  "created_at": "2024-01-01T12:00:00Z"
}
```

### Send WebRTC Signal

Send WebRTC signaling data for call setup.

**Endpoint:** `POST /calls/{call_id}/signal`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "type": "offer",
  "data": {
    "sdp": "v=0\r\no=- ...",
    "type": "offer"
  }
}
```

**Signal types:**
- `offer` - WebRTC offer
- `answer` - WebRTC answer
- `ice-candidate` - ICE candidate

**Response:** `200 OK`
```json
{
  "message": "Signal sent"
}
```

### Get WebRTC Configuration

Get TURN server configuration for WebRTC.

**Endpoint:** `GET /calls/webrtc-config`

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{
  "iceServers": [
    {
      "urls": "stun:stun.l.google.com:19302"
    },
    {
      "urls": "turn:your-turn-server.com:3478",
      "username": "user",
      "credential": "pass"
    }
  ]
}
```

### Get Call History

Get user's call history.

**Endpoint:** `GET /calls/history`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
- `limit` (optional): Number of calls to return (default: 20)

**Response:** `200 OK`
```json
[
  {
    "call_id": "call_xyz789",
    "caller_id": "user_abc123",
    "receiver_id": "user_def456",
    "call_type": "video",
    "status": "ended",
    "started_at": "2024-01-01T12:00:00Z",
    "ended_at": "2024-01-01T12:30:00Z",
    "duration_seconds": 1800,
    "created_at": "2024-01-01T12:00:00Z"
  }
]
```

---

## File Endpoints

### Upload File

Upload a file for sharing in chat.

**Endpoint:** `POST /files/upload`

**Headers:** 
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Request Body:** (multipart/form-data)
- `file`: File to upload

**Allowed extensions:**
- Documents: .pdf, .doc, .docx, .txt, .xlsx, .xls
- Images: .jpg, .jpeg, .png, .gif

**Max file size:** 10MB

**Response:** `200 OK`
```json
{
  "file_id": "file_abc123",
  "original_name": "document.pdf",
  "stored_name": "file_abc123.pdf",
  "size": 1024000,
  "content_type": "application/pdf",
  "uploaded_by": "user_abc123",
  "created_at": "2024-01-01T12:00:00Z",
  "url": "/api/files/file_abc123.pdf"
}
```

### Download File

Download an uploaded file.

**Endpoint:** `GET /files/{filename}`

**Response:** File content with appropriate content-type header

---

## WebSocket API

### Connect

**Endpoint:** `WS /ws/{user_id}`

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/user_abc123');
```

### Message Types

#### Ping/Pong
```json
// Send
{"type": "ping"}

// Receive
{"type": "pong"}
```

#### Join Conversation
```json
{
  "type": "join_conversation",
  "conversation_id": "conv_abc123"
}
```

#### Leave Conversation
```json
{
  "type": "leave_conversation",
  "conversation_id": "conv_abc123"
}
```

#### Typing Indicator
```json
// Start typing
{
  "type": "typing",
  "conversation_id": "conv_abc123"
}

// Stop typing
{
  "type": "stop_typing",
  "conversation_id": "conv_abc123"
}
```

### Received Message Types

#### New Message
```json
{
  "type": "new_message",
  "message": {
    "message_id": "msg_xyz789",
    "content": "Hello!",
    "sender_id": "user_def456",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

#### Incoming Call
```json
{
  "type": "incoming_call",
  "call_id": "call_xyz789",
  "caller_id": "user_def456",
  "caller_name": "Jane Doe",
  "call_type": "video"
}
```

#### Call Status Update
```json
{
  "type": "call_status_update",
  "call_id": "call_xyz789",
  "status": "accepted"
}
```

#### WebRTC Signal
```json
{
  "type": "webrtc_signal",
  "call_id": "call_xyz789",
  "signal_type": "offer",
  "data": {
    "sdp": "v=0...",
    "type": "offer"
  }
}
```

#### User Typing
```json
{
  "type": "user_typing",
  "user_id": "user_def456"
}
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "Email already registered"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid or expired token"
}
```

### 403 Forbidden
```json
{
  "detail": "Not authorized"
}
```

### 404 Not Found
```json
{
  "detail": "User not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## Rate Limiting

Currently no rate limiting is implemented. For production, consider adding rate limiting middleware.

## Pagination

Currently not implemented for most endpoints. Messages and calls use a simple limit parameter.

---

## Health Check

### Health Check Endpoint

**Endpoint:** `GET /api/health`

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

## Examples

### Complete User Registration Flow

```bash
# 1. Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123",
    "full_name": "John Doe",
    "user_type": "student"
  }'

# Response includes token
# {"token": "eyJ0eXAi...", "user": {...}}

# 2. Use token for authenticated requests
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJ0eXAi..."
```

### Send a Message

```bash
curl -X POST http://localhost:8000/api/messages/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "receiver_id": "user_def456",
    "content": "Hello, I need help with my application!"
  }'
```

### Upload and Share File

```bash
# 1. Upload file
curl -X POST http://localhost:8000/api/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@document.pdf"

# Response: {"file_id": "file_abc123", "url": "/api/files/file_abc123.pdf", ...}

# 2. Send message with file
curl -X POST http://localhost:8000/api/messages/send \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "receiver_id": "user_def456",
    "content": "Here is the document you requested",
    "file_url": "/api/files/file_abc123.pdf",
    "file_name": "document.pdf"
  }'
```

---

For more examples and interactive documentation, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
