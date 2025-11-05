# SonarQube Configuration for Hello Django

## Quick Start

1. **Start SonarQube and run analysis:**
   ```bash
   ./sonarqube/setup-sonarqube.sh
   ```

2. **Access SonarQube dashboard:**
   - URL: http://localhost:9000
   - Default credentials: admin/admin

## Manual Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.14+ with virtual environment
- Node.js and npm
- wget and unzip

### Step-by-step Setup

1. **Start SonarQube server:**
   ```bash
   cd sonarqube
   docker-compose up -d
   ```

2. **Wait for SonarQube to be ready (2-3 minutes):**
   ```bash
   curl http://localhost:9000/api/system/status
   # Should return: {"status":"UP"}
   ```

3. **Run backend analysis:**
   ```bash
   cd backend
   source venv/bin/activate
   pip install coverage pytest-django pytest-cov bandit pylint
   
   # Run tests with coverage
   coverage run --source='.' manage.py test
   coverage xml -o coverage.xml
   
   # Security analysis
   bandit -r . -f json -o bandit-report.json --exclude './venv/*'
   
   # Code quality
   pylint --load-plugins=pylint_django $(find . -name "*.py" | grep -v venv) > pylint-report.txt
   ```

4. **Run frontend analysis:**
   ```bash
   cd frontend
   npm install
   npm test -- --coverage --watchAll=false
   ```

5. **Run SonarScanner:**
   ```bash
   # Install SonarScanner if not available
   wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-6.2.1.4610-linux-x64.zip
   unzip sonar-scanner-cli-6.2.1.4610-linux-x64.zip
   export PATH="$PWD/sonar-scanner-6.2.1.4610-linux-x64/bin:$PATH"
   
   # Run analysis
   sonar-scanner -Dsonar.login=admin -Dsonar.password=admin
   ```

## Project Configuration

### sonar-project.properties

The project is configured to analyze:

- **Backend**: Python/Django code in `backend/`
- **Frontend**: TypeScript/React code in `frontend/src/`
- **Tests**: Both backend and frontend test coverage
- **Security**: Bandit security analysis for Python
- **Code Quality**: Pylint for Python, ESLint for TypeScript

### Coverage Reports

- **Backend**: `backend/coverage.xml` (XML format for SonarQube)
- **Frontend**: `frontend/coverage/lcov.info` (LCOV format)

### Quality Gates

Default quality gates include:
- Coverage > 80%
- Duplicated lines < 3%
- Maintainability rating A
- Reliability rating A
- Security rating A

## Docker Compose Services

### SonarQube
- **Image**: sonarqube:community (Latest Community Edition)
- **Port**: 9000
- **Database**: PostgreSQL
- **Volumes**: Persistent data, extensions, and logs

### PostgreSQL
- **Image**: postgres:15
- **Database**: sonar
- **Credentials**: sonar/sonar

## Troubleshooting

### Common Issues

1. **SonarQube won't start:**
   ```bash
   # Check system requirements
   sysctl vm.max_map_count
   # Should be at least 262144
   sudo sysctl -w vm.max_map_count=262144
   ```

2. **Out of memory:**
   ```bash
   # Increase Docker memory limit to at least 4GB
   docker-compose down
   docker system prune
   docker-compose up -d
   ```

3. **Permission issues:**
   ```bash
   sudo chown -R $USER:$USER sonarqube/
   chmod +x sonarqube/setup-sonarqube.sh
   ```

### Logs

Check SonarQube logs:
```bash
docker-compose -f sonarqube/docker-compose.yml logs -f sonarqube
```

Check database logs:
```bash
docker-compose -f sonarqube/docker-compose.yml logs -f sonar-db
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: SonarQube Analysis
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  sonarqube:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.14'
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Run SonarQube Analysis
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
        run: |
          ./sonarqube/setup-sonarqube.sh
```

## Maintenance

### Cleanup

Stop and remove SonarQube:
```bash
cd sonarqube
docker-compose down --volumes
docker system prune
```

### Updates

Update SonarQube:
```bash
cd sonarqube
docker-compose pull
docker-compose down
docker-compose up -d
```

## Security Notes

- Change default admin password after first login
- Configure proper authentication for production
- Use environment variables for sensitive data
- Regularly update SonarQube and scanner versions