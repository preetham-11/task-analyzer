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
- **Responsive design**: Mobile-first approach with breakpoints at 768px and 480px

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

## Algorithm FAQ
 
 ### How do you handle tasks with due dates in the past?
 **Answer:** Tasks with past due dates are treated as **Overdue** and receive the maximum urgency score of **100 points**. However, to keep the system relevant, the frontend prevents adding tasks with due dates **older than 30 days** from today.
 
 ### What if a task has missing or invalid data?
 **Answer:** The system uses **robust default values** and validation:
 - **Missing Importance:** Defaults to 5 (medium importance).
 - **Missing Hours:** Defaults to 2 hours.
 - **Invalid Dates:** The frontend validates dates before submission. If invalid data reaches the backend, it falls back to safe defaults (e.g., today's date).
 - **JSON Errors:** The UI provides specific error messages for invalid JSON structure or syntax errors.
 
 ### How do you detect circular dependencies?
 **Answer:** The backend implements a **Depth-First Search (DFS)** cycle detection algorithm. Before analyzing, it checks the dependency graph. If a cycle is detected (e.g., A -> B -> A), it raises a validation error to prevent infinite loops in the scoring logic.
 
 ### Should your algorithm be configurable?
 **Answer:** **Yes.** The algorithm is designed to be configurable through **Strategies**. Users can select from 4 preset strategies (Smart Balance, Fastest Wins, High Impact, Deadline Driven) which adjust the weights of each component. In a future version, we could expose a "Custom Strategy" UI where users define their own weights (e.g., Urgency 5x, Effort 0x).
 
 ### How do you balance competing priorities (urgent vs important)?
 **Answer:** This is handled by the **Weighted Scoring System**.
 - **Smart Balance Strategy:** Gives equal weight (1x) to both Urgency and Importance. A highly urgent task (100 pts) and a highly important task (100 pts) contribute equally.
 - **Deadline Driven:** Triples the weight of Urgency (3x), so an urgent task will outrank an important one.
 - **High Impact:** Triples the weight of Importance (3x), so a critical task will outrank a merely urgent one.
 
 ---

## Bonus Challenges Attempted

**Multiple Scoring Strategies**: Implemented 4 different strategies (Smart Balance, Fastest Wins, High Impact, Deadline Driven)

**Date Intelligence**: Considers weekends/holidays when calculating urgency

**Comprehensive Testing**: 27 unit tests covering all scoring components, strategies, and prioritization logic

**Responsive UI**: Mobile-friendly design with breakpoints for tablets and phones

---

## Future Improvements

**With More Time:**

1. **Enhanced Features**
   - Task editing
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

---
