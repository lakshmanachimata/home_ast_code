# Home Assistant User Management API

Home Assistant uses **WebSocket API** for user management (not REST API). All operations require **admin privileges**.

## Authentication

All WebSocket commands require:
- A valid WebSocket connection to Home Assistant
- An access token with **admin** privileges
- The connection must be authenticated

## WebSocket Connection

First, establish a WebSocket connection:

```javascript
const ws = new WebSocket('ws://localhost:8123/api/websocket');
ws.onopen = () => {
  // Send auth message
  ws.send(JSON.stringify({
    type: 'auth',
    access_token: 'YOUR_ACCESS_TOKEN'
  }));
};
```

## User Management APIs

### 1. List All Users

**WebSocket Command:**
```json
{
  "id": 1,
  "type": "config/auth/list"
}
```

**Response:**
```json
{
  "id": 1,
  "type": "result",
  "success": true,
  "result": [
    {
      "id": "user_id_1",
      "username": "admin",
      "name": "Administrator",
      "is_owner": true,
      "is_active": true,
      "local_only": false,
      "system_generated": false,
      "group_ids": ["system-admin"],
      "credentials": [{"type": "homeassistant"}]
    }
  ]
}
```

**Python Example:**
```python
import asyncio
import websockets
import json

async def list_users(access_token):
    uri = "ws://localhost:8123/api/websocket"
    async with websockets.connect(uri) as websocket:
        # Authenticate
        auth_msg = {"type": "auth", "access_token": access_token}
        await websocket.send(json.dumps(auth_msg))
        auth_response = await websocket.recv()
        print("Auth:", json.loads(auth_response))
        
        # List users
        list_msg = {
            "id": 1,
            "type": "config/auth/list"
        }
        await websocket.send(json.dumps(list_msg))
        response = await websocket.recv()
        result = json.loads(response)
        return result["result"]

# Usage
users = asyncio.run(list_users("YOUR_ACCESS_TOKEN"))
print(users)
```

**JavaScript Example:**
```javascript
const ws = new WebSocket('ws://localhost:8123/api/websocket');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'auth',
    access_token: 'YOUR_ACCESS_TOKEN'
  }));
};

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  
  if (msg.type === 'auth_ok') {
    // List users
    ws.send(JSON.stringify({
      id: 1,
      type: 'config/auth/list'
    }));
  } else if (msg.id === 1) {
    console.log('Users:', msg.result);
  }
};
```

---

### 2. Create User

**WebSocket Command:**
```json
{
  "id": 2,
  "type": "config/auth/create",
  "name": "John Doe",
  "group_ids": ["system-users"],
  "local_only": false
}
```

**Parameters:**
- `name` (required): Display name for the user
- `group_ids` (optional): List of group IDs (e.g., `["system-admin"]`, `["system-users"]`, `["system-read-only"]`)
- `local_only` (optional): If `true`, user can only authenticate from local network

**Response:**
```json
{
  "id": 2,
  "type": "result",
  "success": true,
  "result": {
    "user": {
      "id": "user_id_2",
      "username": null,
      "name": "John Doe",
      "is_owner": false,
      "is_active": true,
      "local_only": false,
      "system_generated": false,
      "group_ids": ["system-users"],
      "credentials": []
    }
  }
}
```

**Note:** Creating a user only creates the user account. To enable login, you must also create credentials (username/password) using the auth provider API.

**Python Example:**
```python
async def create_user(access_token, name, group_ids=None, local_only=False):
    uri = "ws://localhost:8123/api/websocket"
    async with websockets.connect(uri) as websocket:
        # Authenticate
        await websocket.send(json.dumps({
            "type": "auth",
            "access_token": access_token
        }))
        await websocket.recv()
        
        # Create user
        create_msg = {
            "id": 2,
            "type": "config/auth/create",
            "name": name,
            "group_ids": group_ids or [],
            "local_only": local_only
        }
        await websocket.send(json.dumps(create_msg))
        response = await websocket.recv()
        result = json.loads(response)
        return result["result"]["user"]

# Usage
user = asyncio.run(create_user(
    "YOUR_ACCESS_TOKEN",
    "John Doe",
    group_ids=["system-users"]
))
print(f"Created user: {user['id']}")
```

---

### 3. Create Username/Password Credentials

After creating a user, you need to create credentials (username/password) for them to log in.

**WebSocket Command:**
```json
{
  "id": 3,
  "type": "config/auth_provider/homeassistant/create",
  "user_id": "user_id_2",
  "username": "johndoe",
  "password": "secure_password_123"
}
```

**Parameters:**
- `user_id` (required): The user ID from the create user response
- `username` (required): Username for login
- `password` (required): Password for login

**Response:**
```json
{
  "id": 3,
  "type": "result",
  "success": true,
  "result": null
}
```

**Python Example:**
```python
async def create_credentials(access_token, user_id, username, password):
    uri = "ws://localhost:8123/api/websocket"
    async with websockets.connect(uri) as websocket:
        # Authenticate
        await websocket.send(json.dumps({
            "type": "auth",
            "access_token": access_token
        }))
        await websocket.recv()
        
        # Create credentials
        cred_msg = {
            "id": 3,
            "type": "config/auth_provider/homeassistant/create",
            "user_id": user_id,
            "username": username,
            "password": password
        }
        await websocket.send(json.dumps(cred_msg))
        response = await websocket.recv()
        result = json.loads(response)
        return result["success"]

# Usage
success = asyncio.run(create_credentials(
    "YOUR_ACCESS_TOKEN",
    "user_id_2",
    "johndoe",
    "secure_password_123"
))
print(f"Credentials created: {success}")
```

---

### 4. Delete User

**WebSocket Command:**
```json
{
  "id": 4,
  "type": "config/auth/delete",
  "user_id": "user_id_2"
}
```

**Parameters:**
- `user_id` (required): The user ID to delete

**Response:**
```json
{
  "id": 4,
  "type": "result",
  "success": true,
  "result": null
}
```

**Error Responses:**
- `"no_delete_self"`: Cannot delete your own account
- `"not_found"`: User not found

**Python Example:**
```python
async def delete_user(access_token, user_id):
    uri = "ws://localhost:8123/api/websocket"
    async with websockets.connect(uri) as websocket:
        # Authenticate
        await websocket.send(json.dumps({
            "type": "auth",
            "access_token": access_token
        }))
        await websocket.recv()
        
        # Delete user
        delete_msg = {
            "id": 4,
            "type": "config/auth/delete",
            "user_id": user_id
        }
        await websocket.send(json.dumps(delete_msg))
        response = await websocket.recv()
        result = json.loads(response)
        
        if result.get("success"):
            return True
        else:
            error = result.get("error", {})
            raise Exception(f"Error: {error.get('message', 'Unknown error')}")

# Usage
try:
    success = asyncio.run(delete_user("YOUR_ACCESS_TOKEN", "user_id_2"))
    print("User deleted successfully")
except Exception as e:
    print(f"Error: {e}")
```

---

### 5. Update User

**WebSocket Command:**
```json
{
  "id": 5,
  "type": "config/auth/update",
  "user_id": "user_id_2",
  "name": "Jane Doe",
  "is_active": true,
  "group_ids": ["system-admin"],
  "local_only": false
}
```

**Parameters:**
- `user_id` (required): The user ID to update
- `name` (optional): New display name
- `is_active` (optional): Whether user is active
- `group_ids` (optional): List of group IDs
- `local_only` (optional): Local-only authentication

**Response:**
```json
{
  "id": 5,
  "type": "result",
  "success": true,
  "result": {
    "user": {
      "id": "user_id_2",
      "username": "johndoe",
      "name": "Jane Doe",
      "is_owner": false,
      "is_active": true,
      "local_only": false,
      "system_generated": false,
      "group_ids": ["system-admin"],
      "credentials": [{"type": "homeassistant"}]
    }
  }
}
```

**Error Responses:**
- `"cannot_modify_system_generated"`: Cannot modify system-generated users
- `"cannot_deactivate_owner"`: Cannot deactivate owner account
- `"not_found"`: User not found

**Python Example:**
```python
async def update_user(access_token, user_id, **kwargs):
    uri = "ws://localhost:8123/api/websocket"
    async with websockets.connect(uri) as websocket:
        # Authenticate
        await websocket.send(json.dumps({
            "type": "auth",
            "access_token": access_token
        }))
        await websocket.recv()
        
        # Update user
        update_msg = {
            "id": 5,
            "type": "config/auth/update",
            "user_id": user_id,
            **kwargs
        }
        await websocket.send(json.dumps(update_msg))
        response = await websocket.recv()
        result = json.loads(response)
        return result["result"]["user"]

# Usage
user = asyncio.run(update_user(
    "YOUR_ACCESS_TOKEN",
    "user_id_2",
    name="Jane Doe",
    group_ids=["system-admin"]
))
print(f"Updated user: {user['name']}")
```

---

### 6. Delete Username/Password Credentials

**WebSocket Command:**
```json
{
  "id": 6,
  "type": "config/auth_provider/homeassistant/delete",
  "username": "johndoe"
}
```

**Parameters:**
- `username` (required): Username to delete

**Response:**
```json
{
  "id": 6,
  "type": "result",
  "success": true,
  "result": null
}
```

**Python Example:**
```python
async def delete_credentials(access_token, username):
    uri = "ws://localhost:8123/api/websocket"
    async with websockets.connect(uri) as websocket:
        # Authenticate
        await websocket.send(json.dumps({
            "type": "auth",
            "access_token": access_token
        }))
        await websocket.recv()
        
        # Delete credentials
        delete_msg = {
            "id": 6,
            "type": "config/auth_provider/homeassistant/delete",
            "username": username
        }
        await websocket.send(json.dumps(delete_msg))
        response = await websocket.recv()
        result = json.loads(response)
        return result["success"]

# Usage
success = asyncio.run(delete_credentials("YOUR_ACCESS_TOKEN", "johndoe"))
print(f"Credentials deleted: {success}")
```

---

## Complete Example: Create User with Credentials

```python
import asyncio
import websockets
import json

async def create_user_with_credentials(access_token, name, username, password, group_ids=None):
    """Create a user and set up username/password credentials."""
    uri = "ws://localhost:8123/api/websocket"
    async with websockets.connect(uri) as websocket:
        # Authenticate
        await websocket.send(json.dumps({
            "type": "auth",
            "access_token": access_token
        }))
        auth_response = await websocket.recv()
        print("Auth:", json.loads(auth_response))
        
        # Step 1: Create user
        create_user_msg = {
            "id": 1,
            "type": "config/auth/create",
            "name": name,
            "group_ids": group_ids or ["system-users"],
            "local_only": False
        }
        await websocket.send(json.dumps(create_user_msg))
        user_response = await websocket.recv()
        user_result = json.loads(user_response)
        user_id = user_result["result"]["user"]["id"]
        print(f"Created user: {user_id}")
        
        # Step 2: Create credentials
        create_cred_msg = {
            "id": 2,
            "type": "config/auth_provider/homeassistant/create",
            "user_id": user_id,
            "username": username,
            "password": password
        }
        await websocket.send(json.dumps(create_cred_msg))
        cred_response = await websocket.recv()
        cred_result = json.loads(cred_response)
        print(f"Created credentials: {cred_result['success']}")
        
        return user_id

# Usage
user_id = asyncio.run(create_user_with_credentials(
    "YOUR_ACCESS_TOKEN",
    "John Doe",
    "johndoe",
    "secure_password_123",
    group_ids=["system-users"]
))
print(f"User created with ID: {user_id}")
```

---

## Complete Example: Delete User

```python
async def delete_user_complete(access_token, user_id):
    """Delete a user (credentials are automatically removed)."""
    uri = "ws://localhost:8123/api/websocket"
    async with websockets.connect(uri) as websocket:
        # Authenticate
        await websocket.send(json.dumps({
            "type": "auth",
            "access_token": access_token
        }))
        await websocket.recv()
        
        # Delete user
        delete_msg = {
            "id": 1,
            "type": "config/auth/delete",
            "user_id": user_id
        }
        await websocket.send(json.dumps(delete_msg))
        response = await websocket.recv()
        result = json.loads(response)
        
        if result.get("success"):
            print(f"User {user_id} deleted successfully")
            return True
        else:
            error = result.get("error", {})
            print(f"Error: {error.get('message', 'Unknown error')}")
            return False

# Usage
asyncio.run(delete_user_complete("YOUR_ACCESS_TOKEN", "user_id_2"))
```

---

## User Groups

Common group IDs:
- `"system-admin"`: Administrator (full access)
- `"system-users"`: Regular user
- `"system-read-only"`: Read-only access

---

## Error Handling

All WebSocket commands return error responses in this format:

```json
{
  "id": 1,
  "type": "result",
  "success": false,
  "error": {
    "code": "error_code",
    "message": "Error message"
  }
}
```

Common error codes:
- `"no_delete_self"`: Cannot delete your own account
- `"not_found"`: User not found
- `"cannot_modify_system_generated"`: Cannot modify system-generated users
- `"cannot_deactivate_owner"`: Cannot deactivate owner account

---

## Requirements

- **Admin privileges**: All user management operations require admin access
- **WebSocket connection**: Must use WebSocket API (not REST)
- **Authentication**: Must authenticate with access token before sending commands

---

## Notes

1. **Creating a user** only creates the user account. You must also create credentials (username/password) for the user to log in.

2. **Deleting a user** automatically removes all associated credentials.

3. **You cannot delete your own account** - the API will return an error.

4. **System-generated users** cannot be modified or deleted.

5. **Owner accounts** cannot be deactivated.

