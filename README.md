# Smart Task Analyzer

A mini-application that intelligently scores and prioritizes tasks based on multiple factors including urgency, importance, effort, and dependencies.

## 🔗 Live Demo

- **Frontend**: https://smart-task-analyzer.vercel.app
- **Backend API**: https://smart-task-analyzer.onrender.com
- **GitHub**: https://github.com/808JACK/Smart-Task-Analyzer

> Note: Backend may take 30-60 seconds to start on first request (Render free tier).

## 🛠️ Tech Stack

### Backend
- Python 3.11
- Django 5.2
- Django REST Framework 3.16
- PostgreSQL (Neon)
- Gunicorn
- WhiteNoise

### Frontend
- HTML5
- CSS3
- Vanilla JavaScript

### Deployment
- Backend: Render
- Frontend: Vercel
- Database: Neon (PostgreSQL)

## 🚀 Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/808JACK/Smart-Task-Analyzer.git
cd Smart-Task-Analyzer
```

2. **Install Python dependencies**
```bash
cd backend
pip install -r requirements.txt
```

3. **Run database migrations**
```bash
python manage.py migrate
```

4. **Start the Django development server**
```bash
python manage.py runserver
```

The backend API will be available at `http://localhost:8000`

5. **Open the frontend**
- Open `frontend/index.html` in your web browser
- Or use a simple HTTP server:
```bash
cd frontend
python -m http.server 8080
```
Then visit `http://localhost:8080`

### Running Tests
```bash
cd backend
python manage.py test tasks
```

All 19 tests should pass.

## 📋 Features

### Core Features
- Intelligent task prioritization algorithm with 4 scoring factors (urgency, importance, effort, dependencies)
- 4 different prioritization strategies (Smart Balance, Fastest Wins, High Impact, Deadline Driven)
- REST API with `/analyze` and `/suggest` endpoints
- Interactive frontend with form and JSON bulk input
- Comprehensive error handling and validation

### Bonus Features Implemented

#### 1. Unit Tests ✅
- 19 comprehensive unit tests
- 100% pass rate
- Coverage includes all edge cases

#### 2. Dependency Graph Visualization ✅
- Visual representation of task dependencies
- DFS-based circular dependency detection
- Color-coded warnings for problematic dependencies

#### 3. Date Intelligence ✅
- Weekend detection and business days calculation
- Urgency scores adjusted for tasks due on weekends
- Visual indicators (📅) for weekend tasks

## 🎯 Algorithm Explanation

### Scoring Components

The Smart Task Analyzer uses a weighted scoring system that evaluates tasks across four key dimensions:

**1. Urgency Score (0-100)**
- Calculated based on due date with date intelligence
- Past-due tasks receive maximum urgency (>100)
- Business days calculation excludes weekends
- Weekend penalty applied to tasks due on Saturday/Sunday

**2. Importance Score (0-100)**
- User-provided rating (1-10 scale) normalized to 0-100
- Allows direct influence on prioritization based on business value

**3. Effort Score (0-100)**
- Lower effort tasks receive higher scores (quick wins)
- Tasks < 2 hours: 90 points
- Tasks 2-8 hours: 70-40 points
- Tasks 8+ hours: 30-10 points

**4. Dependency Score (0-100)**
- Tasks that block other tasks receive higher scores
- Base score: 30 points
- +25 points per dependent task (capped at 100)

### Prioritization Strategies

**Smart Balance** (Default)
- Urgency: 35%, Importance: 30%, Effort: 15%, Dependencies: 20%
- Balanced approach considering all factors

**Fastest Wins**
- Urgency: 20%, Importance: 20%, Effort: 50%, Dependencies: 10%
- Prioritizes low-effort tasks for quick completion

**High Impact**
- Urgency: 15%, Importance: 60%, Effort: 10%, Dependencies: 15%
- Focuses on business value and importance

**Deadline Driven**
- Urgency: 60%, Importance: 20%, Effort: 5%, Dependencies: 15%
- Heavily weights due dates to meet deadlines

### Edge Case Handling
- Missing data: Default values applied
- Invalid dates: Neutral urgency score
- Circular dependencies: Detected using DFS and flagged
- Zero/negative hours: Neutral effort score
- Out-of-range importance: Clamped to 1-10

## 📡 API Endpoints

### POST /api/tasks/analyze/
Analyzes and sorts a list of tasks by priority score.

**Request:**
```json
{
  "tasks": [
    {
      "id": "1",
      "title": "Fix login bug",
      "due_date": "2025-11-30",
      "estimated_hours": 3,
      "importance": 8,
      "dependencies": []
    }
  ],
  "strategy": "smart_balance"
}
```

**Response:**
```json
{
  "tasks": [...],
  "strategy": "smart_balance",
  "total_count": 1
}
```

### POST /api/tasks/suggest/
Returns top 3 recommended tasks with explanations.

**Request:** Same as analyze endpoint

**Response:**
```json
{
  "suggestions": [
    {
      "rank": 1,
      "task": {...},
      "explanation": "Ranked #1: Due very soon, marked as highly important. Score: 85.5"
    }
  ],
  "strategy": "smart_balance"
}
```

## 🧪 Testing

Run the test suite:
```bash
cd backend
python manage.py test tasks
```

Expected output: 19 tests pass

## 📁 Project Structure

```
Smart-Task-Analyzer/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── task_analyzer/
│   │   ├── settings.py
│   │   └── urls.py
│   └── tasks/
│       ├── models.py
│       ├── views.py
│       ├── scoring.py
│       ├── urls.py
│       └── tests.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   ├── script.js
│   └── config.js
└── README.md
```

## 📄 License

This project was created as part of a technical assessment for a Software Development Intern position.
