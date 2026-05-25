# 📚 Multi-Agent Gamified Learning System - Complete Setup Guide

## 🎯 Quick Start (5 Minutes)

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (macOS/Linux)
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Application
```bash
python app.py
```

### 4. Access Application
- Open browser: `http://localhost:5000`
- Navigate to Login page
- Create new account
- Explore dashboard!

---

## 📋 Detailed Installation Guide

### Prerequisites
- Python 3.8+
- pip
- Browser (Chrome, Firefox, Safari, Edge)
- 200MB disk space

### Step 1: System Preparation

#### Windows
```bash
# Check Python installation
python --version

# Upgrade pip
python -m pip install --upgrade pip
```

#### macOS/Linux
```bash
# Check Python3 installation
python3 --version

# Upgrade pip
python3 -m pip install --upgrade pip
```

### Step 2: Project Setup

```bash
# Navigate to project directory
cd multi-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

Expected output:
```
Successfully installed Flask-2.3.2 Flask-SQLAlchemy-3.0.5 ...
```

### Step 4: Database Initialization

```bash
python app.py
```

First run creates:
- `gamified_learning.db` - SQLite database
- Sample badges and schema
- All tables initialized

### Step 5: Verify Installation

Access: `http://localhost:5000`

Expected screens:
1. Login page with signup link
2. After signup: Dashboard
3. After login: Full dashboard with challenges

---

## 🔧 Configuration Guide

### Environment Variables (.env)
```env
# Flask Configuration
FLASK_APP=app.py
FLASK_ENV=development
DEBUG=True

# Secret Key (generate: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///gamified_learning.db
# or for MySQL:
# DATABASE_URL=mysql+pymysql://user:password@localhost/gamified_learning

# Session
PERMANENT_SESSION_LIFETIME=604800  # 7 days in seconds

# API Settings
API_TIMEOUT=30
MAX_REQUESTS_PER_MINUTE=60
```

### Database Configuration

#### SQLite (Default)
Already configured, no changes needed.

#### MySQL Setup

1. Install MySQL Server
2. Create database:
```sql
CREATE DATABASE gamified_learning;
CREATE USER 'gamify_user'@'localhost' IDENTIFIED BY 'password';
GRANT ALL PRIVILEGES ON gamified_learning.* TO 'gamify_user'@'localhost';
FLUSH PRIVILEGES;
```

3. Install MySQL driver:
```bash
pip install PyMySQL
```

4. Update `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://gamify_user:password@localhost/gamified_learning'
```

---

## 📊 System Architecture

### Data Flow
```
User Input → Flask Routes → Agents → Database → Response
    ↓           ↓            ↓         ↓          ↓
  Login     Authentication  Analysis  Store    Dashboard
  Activity  Authorization   Generate  Retrieve Analytics
```

### Agent Workflow
```
User Activity
    ↓
Engagement Agent (Analyze)
    ↓
Reward Agent (Generate)
    ↓
Challenge Agent (Create)
    ↓
Optimization Agent (Suggest)
    ↓
Validation Agent (Verify)
    ↓
Diff Viewer (Compare)
    ↓
Database Update
    ↓
User Notification
```

### Database Schema Relationships
```
Users
├── UserActivity (1:N)
├── Challenge (1:N)
├── Reward (1:N)
├── Badge (M:N through user_badges)
└── EngagementMetric (1:N)
```

---

## 🚀 Deployment Guide

### Local Deployment (Development)

```bash
python app.py
```

### Production Deployment (Gunicorn)

1. Install Gunicorn:
```bash
pip install gunicorn
```

2. Run with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. Run with Nginx (optional):
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
ENV FLASK_APP=app.py
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:
```bash
docker build -t gamifylearn .
docker run -p 5000:5000 gamifylearn
```

### Cloud Deployment

#### Heroku
```bash
heroku login
heroku create gamifylearn
git push heroku main
heroku logs --tail
```

#### AWS
1. Create EC2 instance (Ubuntu 20.04)
2. Install Python and dependencies
3. Clone repository
4. Run with Gunicorn + Nginx

#### Google Cloud
1. Create App Engine
2. Update app.yaml
3. Deploy: `gcloud app deploy`

---

## 🔒 Security Best Practices

### 1. Secret Key
Generate strong secret key:
```python
import secrets
print(secrets.token_hex(32))
```

### 2. Password Security
- Minimum 8 characters
- Uses Werkzeug hashing
- Never store plaintext

### 3. HTTPS
In production, always use HTTPS:
```python
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
```

### 4. Database Security
- Use environment variables for credentials
- Regular backups
- SQL injection prevention (SQLAlchemy)
- No hardcoded passwords

### 5. API Security
- CSRF protection enabled
- Rate limiting (implement)
- Input validation
- Output escaping

---

## 🧪 Testing Guide

### Manual Testing

#### Test Login/Signup
1. Navigate to login page
2. Click "Create Account"
3. Fill signup form
4. Verify email validation
5. Login with credentials
6. Verify session

#### Test Engagement Analysis
1. Login as user
2. Click "Analyze Engagement"
3. Complete activities first
4. Verify score calculation
5. Check recommendations

#### Test Challenge Generation
1. Dashboard → Quick Actions
2. Click "Generate Challenges"
3. Verify challenges appear
4. Check difficulty levels
5. Complete a challenge

#### Test Rewards
1. Complete activity
2. Check points increase
3. Verify streak update
4. Check badge unlocks

### Automated Testing (Future)

```python
# test_app.py
import pytest
from app import app, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_signup(client):
    response = client.post('/signup', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123',
        'confirm_password': 'password123'
    })
    assert response.status_code == 302  # Redirect to login

def test_login(client):
    # Create user first
    client.post('/signup', data={...})
    # Test login
    response = client.post('/login', data={
        'username': 'testuser',
        'password': 'password123'
    })
    assert response.status_code == 302  # Redirect to dashboard
```

Run tests:
```bash
pip install pytest pytest-cov
pytest
pytest --cov=app
```

---

## 📊 Performance Optimization

### Database Optimization
```python
# Add indexes
class User(db.Model):
    username = db.Column(db.String(80), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)

# Query optimization
users = User.query.filter_by(is_active=True).limit(50).all()
```

### Caching
```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/api/engagement/score')
@cache.cached(timeout=300)
def engagement_score():
    # This result will be cached for 5 minutes
    pass
```

### Asset Compression
```bash
# Install
pip install flask-compress

# Use
from flask_compress import Compress
Compress(app)
```

---

## 🐛 Debugging Guide

### Enable Debug Mode
```python
app.run(debug=True)
```

### Check Logs
```bash
# Flask debug server shows logs
# For production:
tail -f app.log
```

### Database Debugging
```python
from app import db
# Check tables
db.inspect(db.engine).get_table_names()
# Clear data
db.session.query(User).delete()
db.session.commit()
```

### API Testing
```bash
# Install curl or Postman
# Test endpoint
curl -X POST http://localhost:5000/api/engagement/analyze \
  -H "Content-Type: application/json"
```

---

## 📈 Monitoring & Maintenance

### Regular Maintenance
- **Weekly**: Check error logs
- **Monthly**: Database optimization, backup
- **Quarterly**: Security audit, dependency updates
- **Annually**: Performance review

### Backup Strategy
```bash
# SQLite backup
cp gamified_learning.db gamified_learning.db.backup

# MySQL backup
mysqldump -u user -p database_name > backup.sql

# Schedule backups (crontab)
0 2 * * * /home/user/backup.sh
```

### Monitoring Tools
- **Flask Debugger**: Built-in
- **Sentry**: Error tracking
- **New Relic**: Performance monitoring
- **DataDog**: Full stack monitoring

---

## 📚 Sample Data

### Create Demo User
```python
from app import app, db, User

with app.app_context():
    user = User(
        username='demo',
        email='demo@example.com'
    )
    user.set_password('demo123')
    db.session.add(user)
    db.session.commit()
    print("Demo user created!")
```

### Seed Activities
```python
from app import UserActivity, db
from datetime import datetime, timedelta

with app.app_context():
    for i in range(10):
        activity = UserActivity(
            user_id=1,
            activity_type='quiz',
            activity_name=f'Quiz {i+1}',
            duration_minutes=30,
            points_earned=10,
            status='completed',
            created_at=datetime.utcnow() - timedelta(days=i)
        )
        db.session.add(activity)
    db.session.commit()
```

---

## 🆘 Troubleshooting

### Common Issues

#### Issue: Port Already in Use
```
Address already in use
Solution:
# Find process on port 5000
lsof -i :5000
# Kill process
kill -9 <PID>
# Or use different port
python app.py --port 5001
```

#### Issue: Database Locked
```
sqlite3.OperationalError: database is locked
Solution:
# Delete database file
rm gamified_learning.db
# Restart application
python app.py
```

#### Issue: Import Errors
```
ModuleNotFoundError: No module named 'flask'
Solution:
# Verify virtual environment activated
# Reinstall dependencies
pip install -r requirements.txt
```

#### Issue: Session Cookie Error
```
Solution:
# Set SECRET_KEY in app.py
app.config['SECRET_KEY'] = 'your-secret-key'
```

---

## 📞 Support Resources

### Getting Help
1. Check README.md
2. Review API documentation
3. Check troubleshooting section
4. Review code comments
5. Check Flask documentation

### Useful Links
- [Flask Official Docs](https://flask.palletsprojects.com/)
- [SQLAlchemy Docs](https://docs.sqlalchemy.org/)
- [Python Docs](https://docs.python.org/3/)
- [Bootstrap 5](https://getbootstrap.com/docs/5.0/)

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Production Ready ✅
