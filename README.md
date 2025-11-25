# Smart Task Analyzer

A mini-application that intelligently scores and prioritizes tasks based on multiple factors including urgency, importance, effort, and dependencies.

## Setup Instructions

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation Steps

1. **Clone or download this repository**

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

## Algorithm Explanation

### Overview
The Smart Task Analyzer uses a weighted scoring system that evaluates tasks across four key dimensions: urgency, importance, effort, and dependencies. Each dimension is scored on a 0-100 scale, then combined using configurable weights to produce a final priority score.

### Scoring Components

#### 1. Urgency Score (0-100)
Urgency is calculated based on how soon a task is due:
- **Past due tasks**: Score > 100 (100 + 5 points per day overdue, capped at 200)
- **Due today/tomorrow**: 95 points
- **Due within a week**: 85-71 points (declining by 2 points per day)
- **Due within 2 weeks**: 70-49 points (declining by 3 points per day)
- **Due within a month**: 50-20 points (declining by 2 points per day)
- **Far future (30+ days)**: 5-20 points (slowly declining)

This exponential decay model ensures that imminent deadlines receive appropriate attention while past-due tasks are flagged as critical.

#### 2. Importance Score (0-100)
User-provided importance rating (1-10 scale) is normalized to 0-100:
- Simply multiplied by 10 (e.g., importance 8 = 80 points)
- Allows users to directly influence prioritization based on business value

#### 3. Effort Score (0-100)
Lower effort tasks receive higher scores to identify "quick wins":
- **< 2 hours**: 90 points (quick wins)
- **2-8 hours**: 70-40 points (declining by 5 points per hour)
- **8+ hours**: 30-10 points (declining by 2 points per hour)

This encourages completing smaller tasks that can provide momentum and clear the backlog.

#### 4. Dependency Score (0-100)
Tasks that block other tasks receive higher scores:
- **No dependents**: 30 points (base score)
- **Has dependents**: 30 + (25 × number of dependent tasks), capped at 100

This ensures that bottleneck tasks are prioritized to unblock downstream work.

### Weighting Strategies

The algorithm supports four different prioritization strategies:

#### Smart Balance (Default)
- Urgency: 35%
- Importance: 30%
- Effort: 15%
- Dependencies: 20%

Balanced approach that considers all factors with slight emphasis on urgency and importance.

#### Fastest Wins
- Urgency: 20%
- Importance: 20%
- Effort: 50%
- Dependencies: 10%

Prioritizes low-effort tasks to maximize task completion rate and build momentum.

#### High Impact
- Urgency: 15%
- Importance: 60%
- Effort: 10%
- Dependencies: 15%

Focuses on business value and importance over other factors.

#### Deadline Driven
- Urgency: 60%
- Importance: 20%
- Effort: 5%
- Dependencies: 15%

Heavily weights due dates to ensure deadlines are met.

### Edge Case Handling

1. **Missing Data**: Default values are applied (30 days out, 5 hours, importance 5)
2. **Invalid Dates**: Returns neutral urgency score of 50
3. **Circular Dependencies**: Detected using depth-first search and flagged with warnings
4. **Zero/Negative Hours**: Returns neutral effort score of 50
5. **Out-of-Range Importance**: Clamped to 1-10 range

### Final Score Calculation

```
final_score = (urgency × urgency_weight) + 
              (importance × importance_weight) + 
              (effort × effort_weight) + 
              (dependencies × dependencies_weight)
```

Tasks are then sorted in descending order by final score.

## Design Decisions

### Backend Architecture
- **Django REST Framework**: Chosen for rapid API development with built-in serialization
- **Stateless API**: No database persistence required for core functionality (tasks analyzed on-demand)
- **Modular Design**: Scoring logic separated into dedicated `scoring.py` module for testability
- **Strategy Pattern**: Different weighting strategies implemented as configuration dictionaries

### Frontend Design
- **Vanilla JavaScript**: No framework dependencies for simplicity and fast loading
- **Responsive Design**: Mobile-friendly layout using CSS Grid and Flexbox
- **Visual Hierarchy**: Color-coded priority levels (high/medium/low) and medal system for top 3
- **Dual Input Methods**: Form-based entry for single tasks, JSON bulk import for power users

### Trade-offs Made

1. **No Database Persistence**: Tasks are not saved between sessions
   - **Why**: Simplifies setup and focuses on algorithm demonstration
   - **Future**: Could add SQLite persistence with minimal changes

2. **Client-Side State Management**: Tasks stored in JavaScript array
   - **Why**: Reduces server complexity and API calls
   - **Trade-off**: Data lost on page refresh

3. **CORS Allow All**: Development-only setting for easy frontend testing
   - **Why**: Simplifies local development
   - **Production**: Would restrict to specific origins

4. **Linear Dependency Scoring**: Simple count of dependent tasks
   - **Why**: Easy to understand and compute
   - **Alternative**: Could implement recursive depth scoring for dependency chains

5. **Fixed Strategy Weights**: Predefined weight combinations
   - **Why**: Provides clear, tested strategies
   - **Future**: Could add custom weight sliders for advanced users

## Time Breakdown

- **Algorithm Design & Implementation**: 45 minutes
  - Scoring functions: 25 minutes
  - Circular dependency detection: 15 minutes
  - Strategy system: 5 minutes

- **Backend Development**: 40 minutes
  - Django setup: 10 minutes
  - API endpoints: 15 minutes
  - Error handling: 10 minutes
  - Integration: 5 minutes

- **Unit Tests**: 30 minutes
  - Test case design: 10 minutes
  - Implementation: 15 minutes
  - Edge case coverage: 5 minutes

- **Frontend Development**: 1 hour 15 minutes
  - HTML structure: 20 minutes
  - CSS styling: 30 minutes
  - JavaScript logic: 25 minutes

- **Documentation**: 20 minutes
  - README writing: 15 minutes
  - Code comments: 5 minutes

**Total Time**: ~3 hours 30 minutes

## Bonus Challenges Attempted

None - focused on delivering high-quality core functionality with comprehensive testing and documentation.

## Future Improvements

Given more time, I would implement:

1. **Database Persistence**: Save tasks and analysis history using Django models
2. **User Authentication**: Allow multiple users to manage their own task lists
3. **Dependency Graph Visualization**: D3.js visualization of task dependencies with cycle highlighting
4. **Date Intelligence**: Consider weekends/holidays in urgency calculations
5. **Machine Learning**: Learn from user feedback to adjust weights automatically
6. **Eisenhower Matrix View**: 2D grid visualization of urgent vs important
7. **Export Functionality**: Export prioritized tasks to CSV, JSON, or calendar formats
8. **Real-time Collaboration**: WebSocket support for team task management
9. **Mobile App**: Native iOS/Android apps using React Native
10. **Advanced Filters**: Filter by date range, importance level, or dependency status

## API Endpoints

### POST /api/tasks/analyze/
Analyzes and sorts a list of tasks by priority score.

**Request Body:**
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

**Request Body:** Same as analyze endpoint

**Response:**
```json
{
  "suggestions": [
    {
      "rank": 1,
      "task": {...},
      "explanation": "Ranked #1: Due very soon or overdue, marked as highly important. Score: 85.5"
    }
  ],
  "strategy": "smart_balance"
}
```

## Testing

The project includes 16 comprehensive unit tests covering:
- Urgency score calculations (past due, today, future)
- Effort score calculations (quick, medium, large tasks)
- Importance score normalization
- Dependency score calculations
- Circular dependency detection
- Complete scoring pipeline
- Strategy weight configurations
- Edge case handling (missing data, invalid inputs)

All tests pass successfully.

## Project Structure

```
task-analyzer/
├── backend/
│   ├── manage.py
│   ├── task_analyzer/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── scoring.py
│   │   ├── urls.py
│   │   └── tests.py
│   └── requirements.txt
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── script.js
└── README.md
```

## Technologies Used

- **Backend**: Python 3.11, Django 5.2, Django REST Framework
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Testing**: Django TestCase
- **Database**: SQLite (default Django)

## License

This project was created as part of a technical assessment for a Software Development Intern position.


## Deployment

### Environment Variables

#### Backend (Render)

Set these in Render Dashboard → Environment:

```
SECRET_KEY=<generate-with-command-below>
DEBUG=False
ALLOWED_HOSTS=your-app.onrender.com
CORS_ALLOWED_ORIGINS=https://your-frontend.vercel.app
DATABASE_URL=postgresql://user:pass@host.neon.tech/db?sslmode=require
PORT=3001
```

**Generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### Frontend (Vercel)

Edit `frontend/config.js`:
```javascript
window.ENV = {
    API_URL: 'https://your-backend.onrender.com/api/tasks'
};
```

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push
   ```

2. **Deploy Backend on Render**
   - New Web Service → Connect GitHub repo
   - Root Directory: `backend`
   - Build: `chmod +x build.sh && ./build.sh`
   - Start: `gunicorn task_analyzer.wsgi:application`
   - Add environment variables above

3. **Update Frontend Config**
   - Edit `frontend/config.js` with your Render backend URL
   - Commit and push

4. **Deploy Frontend on Vercel**
   - New Project → Import GitHub repo
   - Output Directory: `frontend`
   - Deploy

5. **Update CORS**
   - Update `CORS_ALLOWED_ORIGINS` in Render with your Vercel URL

### Database Options

- **SQLite** (default): No setup needed, good for development
- **PostgreSQL** (recommended): Set `DATABASE_URL` environment variable with Neon or Render PostgreSQL connection string

## License

This project was created as part of a technical assessment for a Software Development Intern position.
