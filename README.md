# Smart Task Analyzer

A Django-based web application that intelligently prioritizes tasks based on urgency, importance, effort, and dependencies using multiple scoring strategies.

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   cd task_analyzer
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start the development server**
   ```bash
   python manage.py runserver
   ```

6. **Access the application**
   - Open browser to `http://127.0.0.1:8000`
   - API endpoint: `http://127.0.0.1:8000/api/tasks/analyze/`

### Running Tests
```bash
python manage.py test tasks
```

---

## Algorithm Explanation

The Smart Task Analyzer uses a **multi-factor scoring algorithm** to prioritize tasks based on four key components:

### Scoring Components

1. **Urgency (0-100 points)**
   - Overdue/Today: 100 points
   - 1-3 days: 50 points
   - 4-7 days: 25 points
   - 8-14 days: 10 points
   - 15+ days: 0 points

2. **Importance (10-100 points)**
   - User-defined rating (1-10) multiplied by 10
   - Reflects task criticality and impact

3. **Effort (-5 to +15 points)**
   - Quick tasks (<1.5 hrs): +15 bonus
   - Medium tasks (1.5-3 hrs): +5 bonus
   - Long tasks (>3 hrs): -5 penalty
   - Encourages completing quick wins

4. **Dependencies (0-50 points)**
   - Blocks 0 tasks: 0 points
   - Blocks 1 task: +20 points
   - Blocks 2+ tasks: +50 points
   - Prioritizes unblocking other work

### Scoring Strategies

The algorithm supports four strategies that apply different weights to components:

- **Smart Balance**: Equal weights (1x each) - balanced approach
- **Fastest Wins**: Effort 3x, Urgency 0.5x - prioritize quick tasks
- **High Impact**: Importance 3x, Effort 0.5x - focus on critical work
- **Deadline Driven**: Urgency 3x, Effort 0.5x - meet deadlines first

**Final Score** = (Urgency × weight) + (Importance × weight) + (Effort × weight) + (Dependencies × weight)

Tasks are sorted by final score in descending order, with the highest-scoring task recommended first. This approach balances multiple factors while allowing users to choose strategies that match their work style.

---

## Design Decisions

### Architecture
- **Django REST Framework**: Chosen for rapid API development and built-in serialization
- **Separate Frontend**: Vanilla JavaScript for simplicity and no build step required
- **SQLite**: Lightweight database suitable for single-user deployment

### Algorithm Trade-offs
- **Linear scoring vs. exponential**: Linear is more predictable and easier to understand
- **Fixed time buckets**: Simpler than continuous decay functions, good enough for most use cases
- **Effort bonus/penalty**: Encourages quick wins without completely ignoring important long tasks

### UI Decisions
- **No framework**: Vanilla CSS/JS keeps it lightweight and fast
- **Responsive design**: Mobile-first approach with breakpoints at 768px and 480px
- **Minimal animations**: Subtle hover effects only, no distracting motion

### Testing Strategy
- **Component-level tests**: Each scoring function tested independently
- **Integration tests**: Full algorithm tested with realistic scenarios
- **27 test cases**: Focused on critical path, not exhaustive edge cases

---

## Time Breakdown

**Total Time**: ~6 hours

- **Backend Development** (2.5 hours)
  - Django setup and models: 30 min
  - Scoring algorithm implementation: 1 hour
  - API endpoints and validation: 1 hour

- **Frontend Development** (1.5 hours)
  - HTML structure: 20 min
  - CSS styling and responsive design: 50 min
  - JavaScript functionality: 40 min

- **Testing** (1.5 hours)
  - Writing unit tests: 1 hour
  - Debugging and fixing issues: 30 min

- **Documentation & Polish** (0.5 hours)
  - Code comments and README: 30 min

---

## Bonus Challenges Attempted

✅ **Multiple Scoring Strategies**: Implemented 4 different strategies (Smart Balance, Fastest Wins, High Impact, Deadline Driven)

✅ **Comprehensive Testing**: 27 unit tests covering all scoring components, strategies, and prioritization logic

✅ **Responsive UI**: Mobile-friendly design with breakpoints for tablets and phones

---

## Future Improvements

**With More Time:**

1. **Enhanced Features**
   - Task editing and deletion
   - Persistent storage with user accounts
   - Task categories/tags for better organization
   - Calendar integration for due dates

2. **Algorithm Enhancements**
   - Machine learning to learn user preferences
   - Time-of-day awareness (morning vs. evening tasks)
   - Energy level consideration (high/low energy tasks)
   - Historical completion data to improve estimates

3. **UI/UX Improvements**
   - Dark mode toggle
   - Drag-and-drop task reordering
   - Data visualization (charts, graphs)
   - Keyboard shortcuts for power users

4. **Technical Improvements**
   - PostgreSQL for production
   - Caching for faster API responses
   - WebSocket for real-time updates
   - Docker containerization for easy deployment

5. **Testing & Quality**
   - Frontend JavaScript unit tests
   - End-to-end testing with Selenium
   - Performance benchmarking
   - Accessibility audit (WCAG compliance)

---


