# GitHub Copilot Instructions for Django + React Workshop

## Project Context
Following the GitHub Copilot Custom Workshop for Django + React Web development:
https://github.com/ps-copilot-sandbox/copilot-custom-workshop-django-react-web

Building a full-stack web application demonstrating GitHub Copilot capabilities for modern web development with Django backend and React frontend.

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
- Django 5.2+
- Django REST Framework
- PostgreSQL with psycopg2-binary
- JWT Authentication (djangorestframework-simplejwt)
- Django CORS Headers
- python-decouple for environment variables

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

## Workshop Learning Objectives

1. **API Development**: RESTful APIs with Django REST Framework
2. **Frontend Integration**: React components consuming Django APIs  
3. **Database Design**: PostgreSQL with Django ORM
4. **Authentication**: JWT-based authentication system
5. **Testing**: Comprehensive backend and frontend testing
6. **Deployment**: Docker containerization
7. **Copilot Best Practices**: Effective prompting and code generation

## Django Backend Patterns

### Models
```python
from django.db import models
from django.utils import timezone

class Poll(models.Model):
    question = models.CharField(max_length=200)
    pub_date = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-pub_date']
    
    def __str__(self):
        return self.question

class Choice(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
    
    def __str__(self):
        return self.choice_text
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
```

### ViewSets
```python
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Poll, Choice
from .serializers import PollSerializer, ChoiceSerializer

class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.filter(is_active=True)
    serializer_class = PollSerializer
    
    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        poll = self.get_object()
        choice_id = request.data.get('choice_id')
        
        try:
            choice = poll.choices.get(id=choice_id)
            choice.votes += 1
            choice.save()
            return Response({'status': 'vote recorded'})
        except Choice.DoesNotExist:
            return Response(
                {'error': 'Choice not found'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
```

### URL Configuration
```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'polls', views.PollViewSet)

app_name = 'polls'
urlpatterns = [
    path('api/', include(router.urls)),
]
```

## React Frontend Patterns

### Components
```javascript
import React, { useState, useEffect } from 'react';
import { getPollsAPI, voteAPI } from '../services/api';

const PollList = () => {
    const [polls, setPolls] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        fetchPolls();
    }, []);
    
    const fetchPolls = async () => {
        try {
            setLoading(true);
            const response = await getPollsAPI();
            setPolls(response.data);
        } catch (err) {
            setError('Failed to fetch polls');
        } finally {
            setLoading(false);
        }
    };
    
    const handleVote = async (pollId, choiceId) => {
        try {
            await voteAPI(pollId, choiceId);
            fetchPolls();
        } catch (err) {
            setError('Failed to vote');
        }
    };
    
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    
    return (
        <div className="poll-list">
            {polls.map(poll => (
                <PollCard key={poll.id} poll={poll} onVote={handleVote} />
            ))}
        </div>
    );
};

export default PollList;
```

### API Service Layer
```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const getPollsAPI = () => api.get('/polls/');
export const createPollAPI = (data) => api.post('/polls/', data);
export const voteAPI = (pollId, choiceId) => 
    api.post(`/polls/${pollId}/vote/`, { choice_id: choiceId });
```

## Environment Configuration

### Backend Requirements (requirements.txt)
```
Django>=5.2,<5.3
djangorestframework>=3.14
django-cors-headers>=4.3
djangorestframework-simplejwt>=5.3
psycopg2-binary>=2.9
python-decouple>=3.8
black>=23.0
isort>=5.12
```

### Backend Environment (.env)
```
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://workshop_user:workshop_pass@localhost:5432/workshop_db
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Frontend Package.json Dependencies
```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "axios": "^1.3.0",
    "@mui/material": "^5.11.0",
    "@emotion/react": "^11.10.0",
    "@emotion/styled": "^11.10.0"
  },
  "devDependencies": {
    "@testing-library/react": "^13.4.0",
    "@testing-library/jest-dom": "^5.16.0",
    "eslint": "^8.35.0",
    "prettier": "^2.8.0"
  }
}
```

### Docker Configuration
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
    build: ./backend
    container_name: workshop_backend
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://workshop_user:workshop_pass@db:5432/workshop_db
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

## Testing Patterns

### Django Tests
```python
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Poll, Choice

class PollModelTest(TestCase):
    def setUp(self):
        self.poll = Poll.objects.create(question="Test question")
    
    def test_string_representation(self):
        self.assertEqual(str(self.poll), "Test question")

class PollAPITest(APITestCase):
    def setUp(self):
        self.poll = Poll.objects.create(question="Test question")
        self.choice = Choice.objects.create(
            poll=self.poll, 
            choice_text="Test choice"
        )
    
    def test_get_polls(self):
        url = reverse('polls:poll-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_vote(self):
        url = reverse('polls:poll-vote', kwargs={'pk': self.poll.pk})
        data = {'choice_id': self.choice.id}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

### React Tests
```javascript
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import PollList from '../components/PollList';
import * as api from '../services/api';

jest.mock('../services/api');

describe('PollList', () => {
    const mockPolls = [
        {
            id: 1,
            question: 'Test question?',
            choices: [
                { id: 1, choice_text: 'Choice 1', votes: 0 },
                { id: 2, choice_text: 'Choice 2', votes: 0 }
            ]
        }
    ];

    beforeEach(() => {
        api.getPollsAPI.mockResolvedValue({ data: mockPolls });
    });

    test('renders polls correctly', async () => {
        render(<PollList />);
        
        await waitFor(() => {
            expect(screen.getByText('Test question?')).toBeInTheDocument();
        });
    });

    test('handles voting', async () => {
        api.voteAPI.mockResolvedValue({});
        render(<PollList />);
        
        await waitFor(() => {
            const voteButton = screen.getByText('Choice 1');
            fireEvent.click(voteButton);
        });
        
        expect(api.voteAPI).toHaveBeenCalledWith(1, 1);
    });
});
```

## Git Workflow (Conventional Commits)

Format: `<type>(<scope>): <description>`

### Commit Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

### Special Requirement
Include the user prompt as a comment in each commit:

```bash
git commit -m "feat(api): add poll voting endpoint

Implement POST endpoint for voting on poll choices with validation

# User prompt: add voting functionality to the polls API"
```

### Examples
```bash
feat(frontend): add poll list component
fix(backend): handle empty choice validation
docs: update API documentation
test(api): add poll viewset tests
chore(deps): update Django to 5.2.1
```

## Development Workflow

### Phase 1: Project Setup
```bash
# Create project structure
mkdir -p backend frontend database automation

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install django djangorestframework
django-admin startproject mysite .
python manage.py startapp polls

# Frontend setup
cd ../frontend
npx create-react-app .
npm install axios react-router-dom @mui/material

# Database setup
cd ../database
# Create docker-compose.yml for PostgreSQL
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
npm start
```

### Phase 4: Integration & Testing
```bash
# Backend tests
cd backend
python manage.py test

# Frontend tests
cd frontend
npm test

# Docker deployment
cd ..
docker-compose up --build
```

## Copilot Best Practices

### Effective Prompting
1. **Be Specific**: Include context about the workshop and current component
2. **Reference Structure**: Mention the file structure and relationships
3. **Include Examples**: Reference similar patterns already established
4. **Error Context**: When fixing bugs, include error messages

### Example Prompts
```
"Create a Django REST API endpoint for voting on polls following the workshop pattern"

"Add React component for displaying poll results with Material-UI styling"

"Implement JWT authentication for the Django backend with proper middleware"

"Create comprehensive tests for the poll voting functionality"
```

### Incremental Development
1. Start with basic models and serializers
2. Add simple views and URLs
3. Create basic React components
4. Integrate API calls
5. Add authentication
6. Implement advanced features
7. Add comprehensive testing

## Quick Start Commands

### Development Environment
```bash
# Start PostgreSQL
docker-compose -f database/docker-compose.yml up -d

# Backend
cd backend
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver

# Frontend (new terminal)
cd frontend
npm install
npm start
```

### Production Deployment
```bash
# Build and run all services
docker-compose up --build

# Run in background
docker-compose up -d
```

Remember: This workshop demonstrates GitHub Copilot's capabilities in full-stack development. Use clear, specific prompts and build incrementally to get the best results from Copilot.