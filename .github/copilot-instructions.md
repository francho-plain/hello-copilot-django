# GitHub Copilot Instructions for Django + React Workshop

## Project Context
Following the GitHub Copilot Custom Workshop for Django + React Web development:
https://github.com/ps-copilot-sandbox/copilot-custom-workshop-django-react-web

Building a full-stack web application demonstrating GitHub Copilot capabilities for modern web development with Django backend and React frontend.

## Python Version Requirements
- **Python**: 3.14.0 (latest development version)
- **Django**: 5.2+ (compatible with Python 3.14)
- **Environment**: Ubuntu 24.04 LTS recommended

## Code Standards

### Language and Style
- **Language**: All code must be written in English (variables, functions, classes, file names, etc.)
- **Clarity**: Code should be self-explanatory and clean
- **Comments**: Only write comments when strictly necessary to explain complex logic or non-obvious design decisions
- **Python**: Follow PEP 8 strictly
- **JavaScript/React**: Follow standard React conventions and ESLint rules

### Naming Conventions
- **Variables/Functions**: `snake_case` (Python), `camelCase` (JavaScript)
- **Classes**: `PascalCase`
- **Constants**: `UPPER_CASE`
- **Files**: `lowercase_with_underscores.py`, `PascalCase.js` (components)

## Project Structure

```
hello-django/
├── .github/
│   └── copilot-instructions.md
├── .gitignore
├── README.md
├── docker-compose.yml
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── .env
│   ├── mysite/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   └── apps/
│       └── polls/
│           ├── __init__.py
│           ├── admin.py
│           ├── apps.py
│           ├── models.py
│           ├── views.py
│           ├── urls.py
│           ├── serializers.py
│           ├── tests.py
│           └── migrations/
├── frontend/
│   ├── package.json
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── App.js
│   │   └── index.js
│   └── public/
├── database/
│   ├── docker-compose.yml
│   └── init.sql
└── automation/
    ├── deploy.sh
    └── setup.sh
```

## Technology Stack

### Backend
- **Python**: 3.14.0
- **Django**: 5.2+
- **Django REST Framework**: 3.15+
- **PostgreSQL**: 15+ with psycopg2-binary
- **JWT Authentication**: djangorestframework-simplejwt
- **Django CORS Headers**: 4.3+
- **python-decouple**: 3.8+ for environment variables

### Frontend
- React 18+
- Axios for API calls
- React Router for navigation
- Material-UI or Tailwind CSS for styling
- Jest and React Testing Library

### Development Tools
- Docker & Docker Compose
- Git with Conventional Commits
- ESLint & Prettier for JavaScript
- Black and isort for Python
- pyenv for Python version management

## Python 3.14.0 Setup

### Installation with pyenv
```bash
# Install Python 3.14.0 (development version)
pyenv install 3.14.0

# Set for project
cd /home/francho/code/i+d/hello-django
pyenv local 3.14.0

# Verify installation
python --version  # Should show: Python 3.14.0
```

### Backend Environment Setup
```bash
cd backend

# Create virtual environment with Python 3.14.0
python -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip to latest version
pip install --upgrade pip

# Install core dependencies
pip install Django>=5.2,<5.3
pip install djangorestframework>=3.15
pip install django-cors-headers>=4.3
pip install djangorestframework-simplejwt>=5.3
pip install psycopg2-binary>=2.9
pip install python-decouple>=3.8

# Development tools
pip install black>=24.0
pip install isort>=5.13
pip install pytest-django>=4.8

# Generate requirements
pip freeze > requirements.txt
```

## Workshop Learning Objectives

1. **API Development**: RESTful APIs with Django REST Framework
2. **Frontend Integration**: React components consuming Django APIs  
3. **Database Design**: PostgreSQL with Django ORM
4. **Authentication**: JWT-based authentication system
5. **Testing**: Comprehensive backend and frontend testing
6. **Deployment**: Docker containerization
7. **Copilot Best Practices**: Effective prompting and code generation
8. **Python 3.14**: Leverage latest Python features

## Django Backend Patterns

### Models (Using Python 3.14 features)
```python
from django.db import models
from django.utils import timezone
from typing import Self

class Poll(models.Model):
    question: str = models.CharField(max_length=200)
    pub_date: timezone.datetime = models.DateTimeField(default=timezone.now)
    is_active: bool = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-pub_date']
    
    def __str__(self) -> str:
        return self.question
    
    @classmethod
    def active_polls(cls) -> models.QuerySet[Self]:
        return cls.objects.filter(is_active=True)

class Choice(models.Model):
    poll: Poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='choices')
    choice_text: str = models.CharField(max_length=200)
    votes: int = models.IntegerField(default=0)
    
    def __str__(self) -> str:
        return self.choice_text
    
    def increment_vote(self) -> None:
        self.votes += 1
        self.save()
```

### Serializers
```python
from rest_framework import serializers
from .models import Poll, Choice

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'choice_text', 'votes']

class PollSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    
    class Meta:
        model = Poll
        fields = ['id', 'question', 'pub_date', 'is_active', 'choices']
    
    def validate_question(self, value: str) -> str:
        if len(value.strip()) < 5:
            raise serializers.ValidationError("Question must be at least 5 characters long")
        return value.strip()
```

### ViewSets (Enhanced with Python 3.14)
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django.db import transaction
from .models import Poll, Choice
from .serializers import PollSerializer, ChoiceSerializer

class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.active_polls()
    serializer_class = PollSerializer
    
    @action(detail=True, methods=['post'])
    def vote(self, request: Request, pk: str = None) -> Response:
        poll = self.get_object()
        choice_id = request.data.get('choice_id')
        
        if not choice_id:
            return Response(
                {'error': 'choice_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                choice = poll.choices.select_for_update().get(id=choice_id)
                choice.increment_vote()
                
            return Response({
                'status': 'vote recorded',
                'choice': ChoiceSerializer(choice).data
            })
        except Choice.DoesNotExist:
            return Response(
                {'error': 'Choice not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['get'])
    def results(self, request: Request, pk: str = None) -> Response:
        poll = self.get_object()
        total_votes = sum(choice.votes for choice in poll.choices.all())
        
        results = {
            'poll': PollSerializer(poll).data,
            'total_votes': total_votes,
            'results': [
                {
                    'choice': choice.choice_text,
                    'votes': choice.votes,
                    'percentage': (choice.votes / total_votes * 100) if total_votes > 0 else 0
                }
                for choice in poll.choices.all().order_by('-votes')
            ]
        }
        
        return Response(results)
```

## Environment Configuration

### Backend Requirements (requirements.txt)
```
Django>=5.2,<5.3
djangorestframework>=3.15
django-cors-headers>=4.3
djangorestframework-simplejwt>=5.3
psycopg2-binary>=2.9
python-decouple>=3.8
black>=24.0
isort>=5.13
pytest-django>=4.8
pytest-cov>=4.0
```

### Backend Environment (.env)
```
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://workshop_user:workshop_pass@localhost:5432/workshop_db
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0
PYTHON_VERSION=3.14.0
```

### Docker Configuration (Updated for Python 3.14)
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    container_name: workshop_postgres
    environment:
      POSTGRES_DB: workshop_db
      POSTGRES_USER: workshop_user
      POSTGRES_PASSWORD: workshop_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    container_name: workshop_backend
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://workshop_user:workshop_pass@db:5432/workshop_db
      - PYTHON_VERSION=3.14.0
    volumes:
      - ./backend:/app

  frontend:
    build: ./frontend
    container_name: workshop_frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app

volumes:
  postgres_data:
```

### Backend Dockerfile (Python 3.14)
```dockerfile
FROM python:3.14-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

## Development Workflow

### Phase 1: Python 3.14 Setup
```bash
# Install Python 3.14.0
pyenv install 3.14.0
cd /home/francho/code/i+d/hello-django
pyenv local 3.14.0

# Verify Python version
python --version  # Should show Python 3.14.0

# Create backend environment
cd backend
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Phase 2: Backend Development
```bash
cd backend
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Phase 3: Frontend Development
```bash
cd frontend
npm install
npm start
```

### Phase 4: Testing with Python 3.14
```bash
# Backend tests with pytest
cd backend
pytest --cov=apps/polls --cov-report=html

# Django tests
python manage.py test

# Frontend tests
cd frontend
npm test
```

## Python 3.14 Specific Features

### Enhanced Type Hints
```python
from typing import Self, TypeVar, Generic
from collections.abc import Sequence

T = TypeVar('T')

class PollManager(Generic[T]):
    def filter_active(self, polls: Sequence[T]) -> list[T]:
        return [poll for poll in polls if poll.is_active]
```

### Improved Error Messages
```python
def vote_on_poll(poll_id: int, choice_id: int) -> dict[str, Any]:
    try:
        poll = Poll.objects.get(id=poll_id)
        choice = poll.choices.get(id=choice_id)
        choice.increment_vote()
        return {'status': 'success', 'votes': choice.votes}
    except Poll.DoesNotExist as e:
        raise ValueError(f"Poll {poll_id} not found") from e
    except Choice.DoesNotExist as e:
        raise ValueError(f"Choice {choice_id} not found in poll {poll_id}") from e
```

## Git Workflow (Conventional Commits)

Format: `<type>(<scope>): <description>`

### Commit Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semi colons, etc)
- `refactor`: Code refactoring (no functional changes)
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks (updating dependencies, build tools, etc)
- `perf`: Performance improvements
- `ci`: Changes to CI configuration files and scripts
- `build`: Changes that affect the build system

### Special Requirement - User Prompts History
Include ONLY meaningful user prompts since the last commit as comments in the commit message. 

**Exclude procedural prompts** such as:
- "haz commit" / "make commit" / "commit changes"
- "run tests" / "check status"
- "fix typo" / "format code"
- Basic navigation or file operations

**Include substantive prompts** such as:
- Feature requests and implementations
- Bug reports and fixes
- Configuration changes
- Architecture decisions
- Documentation updates
- Technical questions and solutions

```bash
git commit -m "feat(api): add poll voting endpoint

Implement POST endpoint for voting on poll choices with validation
- Add vote action to PollViewSet
- Include error handling for invalid choices
- Update API documentation

# User prompts since last commit:
# 1. add voting functionality to the polls API
# 2. handle error cases when choice doesn't exist
# 3. update the API docs
# (excluded: 'haz commit', 'run the server')"
```

### Complete Commit Format Template
```bash
<type>(<scope>): <short description (50 chars max)>

<detailed description explaining what and why>
- Bullet point of change 1
- Bullet point of change 2
- Bullet point of change 3

# User prompts since last commit:
# 1. <first meaningful prompt>
# 2. <second meaningful prompt>
# 3. <third meaningful prompt>
# ... (continue for all substantive prompts)
# (excluded: procedural prompts like 'haz commit', 'run tests')
```

### Examples with User Prompts
```bash
feat(database): add PostgreSQL cats database setup

Create complete database infrastructure with sample data
- Add Dockerfile for PostgreSQL 15 container
- Create docker-compose.yml with health checks
- Include create-data.sql with 15 sample cat records
- Add comprehensive documentation

# User prompts since last commit:
# 1. Can you help me to create a Dockerfile that helps to run on localhost
# 2. Create a new PostgreSQL database table called "cats"
# 3. Insert more than 10 random data representing different cats
# (excluded: 'haz commit', 'run the server')

fix(backend): resolve database connection timeout

Update connection pool settings and add retry logic
- Increase connection timeout to 30 seconds
- Add automatic retry on connection failure
- Update error logging for better debugging

# User prompts since last commit:
# 1. the database keeps timing out
# 2. add retry logic for failed connections
# 3. improve error messages
# (excluded: 'check status', 'run tests')

docs: update README with setup instructions

Enhance documentation for better developer onboarding
- Add step-by-step installation guide
- Include troubleshooting section
- Add examples for common use cases

# User prompts since last commit:
# 1. update the README with better instructions
# 2. add troubleshooting section
# (excluded: 'make commit', 'format code')
```

### Scope Guidelines
- **backend**: Django backend changes
- **frontend**: React frontend changes
- **database**: Database schema, migrations, or data changes
- **api**: API endpoints and serializers
- **auth**: Authentication and authorization
- **tests**: Test files and testing configuration
- **docs**: Documentation updates
- **ci**: Continuous integration changes
- **docker**: Container and deployment configuration

### Breaking Changes
For breaking changes, add `!` after the type/scope:

```bash
feat(api)!: change user authentication endpoint

Modify authentication to use JWT tokens instead of sessions
- BREAKING: Remove session-based authentication
- Add JWT token generation and validation
- Update all API endpoints to require JWT header

# User prompts since last commit:
# 1. switch to JWT authentication
# 2. remove session-based auth completely
```

### Commit Message Best Practices
1. **Subject line**: 50 characters or less, imperative mood
2. **Body**: Explain what and why, not how
3. **User prompts**: Include all prompts since last commit
4. **Breaking changes**: Clearly marked with `!` and described
5. **Co-authors**: Use `Co-authored-by:` for pair programming

Include the user prompt as a comment in each commit:

```bash
git commit -m "feat(backend): upgrade to Python 3.14.0

Update Django models and views to use Python 3.14 features
- Enhanced type hints with Self and TypeVar
- Improved error handling
- Updated requirements.txt

# User prompts since last commit:
# 1. vamos a usar python 3.14.0 actualiza instrucciones"
```

## Quick Start Commands (Python 3.14)

### Complete Setup
```bash
# 1. Install Python 3.14.0
pyenv install 3.14.0
cd /home/francho/code/i+d/hello-django
pyenv local 3.14.0

# 2. Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install Django>=5.2 djangorestframework>=3.15
pip install django-cors-headers djangorestframework-simplejwt
pip install psycopg2-binary python-decouple
pip install black isort pytest-django
pip freeze > requirements.txt

# 3. Start PostgreSQL
docker-compose -f database/docker-compose.yml up -d

# 4. Django setup
django-admin startproject mysite .
python manage.py startapp apps/polls
python manage.py migrate
python manage.py runserver

# 5. Frontend (new terminal)
cd frontend
npx create-react-app .
npm install axios react-router-dom @mui/material
npm start
```

### Verification Commands
```bash
# Verify Python version
python --version  # Should show: Python 3.14.0

# Verify Django
python -c "import django; print(f'Django {django.get_version()}')"

# Verify all services
curl http://localhost:8000/api/polls/  # Django API
curl http://localhost:3000/           # React frontend
```

Remember: Python 3.14.0 is in development, so ensure compatibility with all dependencies and be prepared for potential alpha/beta issues.