# Community Creation Scripts

This directory contains Python scripts to create new communities in the PyNewsServer database with properly hashed passwords.

## Available Scripts

### 1. `create_community.py` - Command Line Script

**Usage:**
```bash
python scripts/create_community.py <username> <email> <password>
```

**Example:**
```bash
python scripts/create_community.py john_doe john@example.com mypassword123
```

**Features:**
- Takes command line arguments for username, email, and password
- Automatically hashes the password using the `hash_password` function from `app.services.auth`
- Creates the community record in the database
- Returns success confirmation with community details

### 2. `add_community.py` - Interactive Script

**Usage:**
```bash
python scripts/add_community.py
```

**Features:**
- Interactive prompt for username, email, and password input
- Confirmation step before creating the community
- Password is hidden in the confirmation display
- Uses the same `hash_password` function for security

### 3. `example_create_community.py` - Example/Demo Script

**Usage:**
```bash
python scripts/example_create_community.py
```

**Features:**
- Demonstrates how to create a community programmatically
- Shows the password hashing process step by step
- Good for understanding the implementation
- Creates a sample community with hardcoded values

## Important Notes

### Security
- All scripts use the `hash_password` function from `app.services.auth`
- Passwords are hashed using bcrypt with salt before storage
- Plain text passwords are never stored in the database

### Database
- Scripts automatically initialize the database if it doesn't exist
- Uses the same async database session management as the main application
- All database operations are handled asynchronously

### Requirements
- Python virtual environment must be activated
- All dependencies from `requirements.txt` must be installed
- Scripts must be run from the project root directory

## Running with Virtual Environment

If you have a virtual environment set up (recommended):

```bash
# Activate the virtual environment first
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate     # On Windows

# Then run any script
python scripts/create_community.py username email password
```

Or use the full path to the Python executable:

```bash
/path/to/your/project/.venv/bin/python scripts/create_community.py username email password
```

## Example Output

```
Creating community for user: john_doe
✅ Community created successfully!
   ID: 1
   Username: john_doe
   Email: john@example.com
   Created at: 2025-10-14 12:02:15.778722
```

## Integration with Main Application

These scripts use the same:
- Database models (`app.services.database.models.communities.Community`)
- Authentication functions (`app.services.auth.hash_password`)
- Database session management (`app.services.database.database`)

This ensures consistency with the main application's authentication and data handling.

````
