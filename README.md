# Django + React Workshop - Polls Application

A full-stack web application demonstrating GitHub Copilot capabilities for modern web development. This project follows the [GitHub Copilot Custom Workshop for Django + React](https://github.com/ps-copilot-sandbox/copilot-custom-workshop-django-react-web) and builds a comprehensive polls application with Django REST Framework backend and React frontend.

## 🎯 Project Overview

This project showcases:
- **Backend**: Django REST API with PostgreSQL
- **Frontend**: React application consuming Django APIs
- **Authentication**: JWT-based authentication system
- **Database**: PostgreSQL with Docker containerization
- **Testing**: Comprehensive backend and frontend testing
- **DevOps**: Docker deployment and automation scripts

## 🏗️ Architecture

```
┌─────────────┐    HTTP/REST API    ┌─────────────┐    SQL Queries    ┌─────────────┐
│   React     │ ←─────────────────→ │   Django    │ ←──────────────→ │ PostgreSQL  │
│  Frontend   │                     │   Backend   │                   │  Database   │
│  (Port 3000)│                     │ (Port 8000) │                   │ (Port 5432) │
└─────────────┘                     └─────────────┘                   └─────────────┘
```

## 📁 Project Structure

```
hello-django/
├── .github/
│   └── copilot-instructions.md    # GitHub Copilot custom instructions
├── backend/                       # Django REST API application
│   ├── manage.py                  # Django management script
│   ├── requirements.txt           # Python dependencies
│   ├── .env                       # Environment variables
│   ├── mysite/                    # Django project settings
│   │   ├── settings.py           # Main configuration
│   │   ├── urls.py               # URL routing
│   │   └── wsgi.py               # WSGI application
│   └── apps/
│       └── polls/                 # Polls application
│           ├── models.py         # Data models
│           ├── views.py          # API views
│           ├── serializers.py    # DRF serializers
│           ├── urls.py           # App URL patterns
│           └── tests.py          # Unit tests
├── frontend/                      # React application
│   ├── package.json              # Node.js dependencies
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── services/             # API service layer
│   │   ├── App.js               # Main application
│   │   └── index.js             # Application entry point
│   └── public/                   # Static assets
├── database/                      # Database configuration
│   └── docker-compose.yml        # PostgreSQL container setup
├── automation/                    # Deployment scripts
│   ├── deploy.sh                 # Production deployment
│   └── setup.sh                  # Development setup
├── docker-compose.yml             # Multi-service orchestration
├── .gitignore                     # Git ignore patterns
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- Git

### 1. Clone and Setup

```bash
git clone <repository-url>
cd hello-django
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create Django project and app
django-admin startproject mysite .
python manage.py startapp polls

# Apply migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

The Django development server will be available at http://localhost:8000

### 3. Database Setup

```bash
# Navigate to database directory
cd database

# Start PostgreSQL with Docker
docker-compose up -d

# Verify database is running
docker-compose logs postgres
```

### 4. Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Create React application
npx create-react-app .

# Install additional dependencies
npm install axios react-router-dom @mui/material @emotion/react @emotion/styled

# Start development server
npm start
```

The React development server will be available at http://localhost:3000

### 5. Full Stack with Docker

```bash
# From project root
docker-compose up --build

# Run in background
docker-compose up -d
```

## 🛠️ Development Workflow

### Backend Development

```bash
cd backend

# Activate virtual environment
source venv/bin/activate

# Make and apply migrations
python manage.py makemigrations
python manage.py migrate

# Run tests
python manage.py test

# Run development server
python manage.py runserver
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

### Database Management

```bash
# Start database
docker-compose -f database/docker-compose.yml up -d

# Access database shell
docker exec -it polls_postgres psql -U postgres -d polls_db

# Stop database
docker-compose -f database/docker-compose.yml down
```

## 🧪 Testing

### Backend Tests

```bash
cd backend
python manage.py test polls
python manage.py test --coverage
```

### Frontend Tests

```bash
cd frontend
npm test
npm test -- --coverage
```

## 📦 Dependencies

### Backend (Python)

- Django 5.2+
- Django REST Framework
- Django CORS Headers
- JWT Authentication
- PostgreSQL adapter (psycopg2)
- Environment management (python-decouple)

### Frontend (JavaScript)

- React 18+
- React Router DOM
- Axios (HTTP client)
- Material-UI (UI components)
- Jest & React Testing Library

### Development Tools

- Docker & Docker Compose
- ESLint & Prettier
- Black (Python formatter)
- Git with Conventional Commits

## 🔧 Configuration

### Environment Variables

Create `.env` file in the backend directory:

```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://postgres:password@localhost:5432/polls_db
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Docker Environment

The project includes Docker configuration for:
- PostgreSQL database
- Django backend
- React frontend
- Nginx (production)

## 🚦 API Endpoints

### Polls API

```
GET    /api/polls/           # List all polls
POST   /api/polls/           # Create new poll
GET    /api/polls/{id}/      # Get specific poll
PUT    /api/polls/{id}/      # Update poll
DELETE /api/polls/{id}/      # Delete poll
POST   /api/polls/{id}/vote/ # Vote on poll
```

### Authentication API

```
POST   /api/auth/login/      # User login
POST   /api/auth/logout/     # User logout
POST   /api/auth/register/   # User registration
POST   /api/auth/refresh/    # Refresh JWT token
```

## 🎓 Learning Objectives

This workshop demonstrates:

1. **API Development**: Building RESTful APIs with Django REST Framework
2. **Frontend Integration**: Creating React components that consume Django APIs
3. **Database Design**: Modeling data with Django ORM and PostgreSQL
4. **Authentication**: Implementing JWT-based authentication
5. **Testing**: Writing comprehensive unit and integration tests
6. **Deployment**: Containerizing applications with Docker
7. **GitHub Copilot**: Effective AI-assisted development practices

## 🤝 Contributing

### Git Workflow

This project uses Conventional Commits. Format:

```
<type>(<scope>): <description>

# User prompt: <original user request>
```

Example:
```bash
git commit -m "feat(api): add poll voting endpoint

Implement POST endpoint for voting on poll choices with validation

# User prompt: add voting functionality to the polls API"
```

### Commit Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or modifying tests
- `chore`: Maintenance tasks

## 📖 Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://reactjs.org/)
- [GitHub Copilot Workshop](https://github.com/ps-copilot-sandbox/copilot-custom-workshop-django-react-web)
- [Conventional Commits](https://www.conventionalcommits.org/)

## 📄 License

This project is part of the GitHub Copilot Custom Workshop and is intended for educational purposes.

## 🆘 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Ensure PostgreSQL is running
docker-compose -f database/docker-compose.yml ps

# Check database logs
docker-compose -f database/docker-compose.yml logs postgres
```

**CORS Issues**
```bash
# Verify CORS settings in Django settings.py
# Ensure frontend URL is in CORS_ALLOWED_ORIGINS
```

**Module Not Found**
```bash
# Backend: Activate virtual environment
source backend/venv/bin/activate

# Frontend: Install dependencies
cd frontend && npm install
```

### Getting Help

1. Check the [GitHub Copilot Workshop documentation](https://github.com/ps-copilot-sandbox/copilot-custom-workshop-django-react-web)
2. Review the custom instructions in `.github/copilot-instructions.md`
3. Use GitHub Copilot Chat for context-aware assistance
4. Check Django and React official documentation

---

**Built with ❤️ using GitHub Copilot** | **Follow the workshop to learn AI-assisted development**