# EGG Monitor - Technical Context

## Technologies
- **Frontend**:
  - NextJS 14 (strictly no NextJS15)
  - d3.js (latest version)
  - Tailwind CSS
- **Backend**:
  - Python 3.11
  - FastAPI
  - WebSockets
- **Database**:
  - SQLite
- **DevOps**:
  - Docker
  - Docker Compose

## Development Setup
1. **Requirements**:
   - Docker and Docker Compose installed
   - Node.js (version compatible with NextJS14)
   - Python 3.11

2. **Constraints**:
   - Frontend must use NextJS14 (not 15)
   - Backend must use Python 3.11
   - SQLite is mandatory for database
   - All services must be dockerized

3. **Tooling**:
   - Backend requires unit tests
   - Frontend requires integration tests
   - GitHub for version control
