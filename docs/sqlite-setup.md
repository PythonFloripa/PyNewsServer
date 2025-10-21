# SQLite Service Setup

This document describes the SQLite service configuration for the PyNewsServer project.

## Overview

The SQLite service is configured as part of the Docker Compose setup to provide persistent database storage for the application.

## Architecture

- **sqlite-init**: An initialization service that creates the SQLite database file and sets proper permissions
- **pynews-api**: The main application service that connects to the SQLite database
- **sqlite_data volume**: A bind mount volume that maps to `./data` directory for data persistence

## Configuration

### Environment Variables

The following environment variables are used for SQLite configuration:

- `SQLITE_PATH`: Path to the SQLite database file (default: `/app/data/pynewsdb.db`)
- `SQLITE_URL`: SQLAlchemy connection URL (default: `sqlite+aiosqlite:///app/data/pynewsdb.db`)

### Volume Mapping

- **Host Path**: `./data`
- **Container Path**: `/app/data`
- **Database File**: `pynewsdb.db`

## Services

### sqlite-init

This service:
- Creates the data directory if it doesn't exist
- Creates an empty SQLite database file
- Sets proper file permissions (664)
- Sets proper ownership (1000:1000)
- Runs only once and exits

### pynews-api

The main application service:
- Depends on `sqlite-init` to ensure database initialization
- Mounts the SQLite data volume
- Uses async SQLite operations via `aiosqlite`
- Automatically creates tables on first run

## Usage

### Starting the Services

```bash
docker-compose up -d
```

This will:
1. Start the `sqlite-init` service to initialize the database
2. Start the `pynews-api` service after initialization is complete

### Accessing the Database

The SQLite database file is located at:
- **Host**: `./data/pynewsdb.db`
- **Container**: `/app/data/pynewsdb.db`

### Database Operations

The application uses SQLModel with async SQLAlchemy for database operations:

- **Connection**: Async SQLite with `aiosqlite`
- **ORM**: SQLModel (built on SQLAlchemy)
- **Sessions**: Async session management
- **Migrations**: Automatic table creation via SQLModel metadata

## Data Persistence

Database data is persisted in the `./data` directory on the host system. This directory is:
- Created automatically by the services
- Excluded from Git via `.gitignore`
- Bound to the container's `/app/data` directory

## Backup and Recovery

### Backup

```bash
# Copy database file
cp ./data/pynewsdb.db ./data/pynewsdb.db.backup

# Or use SQLite dump
sqlite3 ./data/pynewsdb.db .dump > backup.sql
```

### Recovery

```bash
# Restore from backup file
cp ./data/pynewsdb.db.backup ./data/pynewsdb.db

# Or restore from SQL dump
sqlite3 ./data/pynewsdb.db < backup.sql
```

## Troubleshooting

### Permission Issues

If you encounter permission issues:

```bash
# Fix ownership
sudo chown 1000:1000 ./data/pynewsdb.db

# Fix permissions
chmod 664 ./data/pynewsdb.db
```

### Database Corruption

If the database becomes corrupted:

```bash
# Remove corrupted database
rm ./data/pynewsdb.db

# Restart services to recreate
docker-compose restart
```

### Volume Issues

If volume mounting fails:

```bash
# Ensure data directory exists
mkdir -p ./data

# Check Docker permissions
ls -la ./data/
```
