# 🔌 Multi-Agent Gamified Learning System - API Reference

## API Overview

**Base URL**: `http://localhost:5000`  
**Authentication**: Flask-Login Session (Cookie-based)  
**Response Format**: JSON  
**Status Codes**: Standard HTTP codes  

---

## 🔐 Authentication Endpoints

### Login
```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=testuser&password=password123

Response:
- Success: Redirect to /dashboard
- Failure: Redirect to /login with error message
```

### Signup
```http
POST /signup
Content-Type: application/x-www-form-urlencoded

username=newuser&email=user@example.com&password=pass123&confirm_password=pass123

Response:
- Success: Redirect to /login with success message
- Failure: Redirect to /signup with error message
```

### Logout
```http
GET /logout
Response: Redirect to /login
```

---

## 📊 Engagement Agent API

### Analyze Engagement
```http
POST /api/engagement/analyze
Authorization: Session required

Response:
{
  "status": "success",
  "data": {
    "engagement_score": 75.5,
    "activities_count": 12,
    "total_time_minutes": 480,
    "daily_active": true,
    "activity_breakdown": {
      "quiz": 5,
      "challenge": 4,
      "study": 3
    },
    "streak_info": {
      "current": 7,
      "longest": 14
    },
    "recommendations": [
      "Keep up the good work! Consistency is key.",
      "Try completing some quizzes to improve learning"
    ],
    "analysis_timestamp": "2024-01-15T10:30:00"
  }
}
```

### Get Engagement Score
```http
GET /api/engagement/score
Authorization: Session required

Response:
{
  "status": "success",
  "engagement_score": 75.5
}
```

---

## 🎯 Challenge Agent API

### Generate Challenges
```http
POST /api/challenges/generate
Authorization: Session required

Response:
{
  "status": "success",
  "challenges": {
    "total_challenges": 3,
    "recommended_count": 3,
    "challenges": [
      {
        "type": "daily",
        "title": "Daily Grind",
        "description": "Complete at least one learning activity today",
        "difficulty": "easy",
        "points": 10,
        "days_to_complete": 1,
        "tasks": ["Log in", "Complete one quiz", "Spend 15 minutes"],
        "xp_reward": 50
      }
    ],
    "motivation_message": "You're crushing it!",
    "generated_at": "2024-01-15T10:30:00"
  }
}
```

### Get Active Challenges
```http
GET /api/challenges/active
Authorization: Session required

Response:
{
  "status": "success",
  "challenges": [
    {
      "id": 1,
      "title": "Weekly Challenge",
      "description": "Complete 3 quizzes",
      "difficulty_level": "medium",
      "points_reward": 50,
      "status": "active",
      "created_at": "2024-01-14T10:00:00",
      "due_date": "2024-01-21T10:00:00"
    }
  ]
}
```

### Complete Challenge
```http
POST /api/challenges/complete/{challenge_id}
Authorization: Session required

Response:
{
  "status": "success",
  "message": "Challenge completed! You earned 50 points",
  "new_balance": 350
}
```

---

## 🏆 Reward Agent API

### Generate Rewards
```http
POST /api/rewards/generate
Authorization: Session required
Content-Type: application/json

{
  "activity_type": "quiz",
  "points_earned": 10
}

Response:
{
  "status": "success",
  "rewards": {
    "rewards": [
      {
        "type": "points",
        "name": "Quiz Reward",
        "amount": 15,
        "description": "Points for completing quiz"
      },
      {
        "type": "bonus",
        "name": "5-Day Streak Bonus",
        "amount": 10,
        "description": "Bonus for 5 day streak"
      }
    ],
    "total_points": 25,
    "total_reward_type": "mixed",
    "reward_summary": "Earned 25 points and 1 bonus rewards!",
    "generated_at": "2024-01-15T10:30:00"
  }
}
```

### Get Reward History
```http
GET /api/rewards/history
Authorization: Session required

Response:
{
  "status": "success",
  "rewards": [
    {
      "id": 1,
      "type": "points",
      "amount": 50,
      "reason": "challenge",
      "created_at": "2024-01-14T15:30:00"
    },
    {
      "id": 2,
      "type": "badge",
      "amount": 0,
      "reason": "milestone",
      "created_at": "2024-01-14T14:20:00"
    }
  ]
}
```

---

## 💡 Optimization Agent API

### Get Optimization Suggestions
```http
GET /api/optimization/suggest
Authorization: Session required

Response:
{
  "status": "success",
  "suggestions": [
    {
      "category": "Activity Pattern",
      "priority": "high",
      "suggestion": "You're most active on Mondays. Try to add activity on other days too.",
      "potential_impact": "High",
      "estimated_points": 75,
      "action": "Increase activity frequency to 4+ days per week"
    },
    {
      "category": "Time Investment",
      "priority": "medium",
      "suggestion": "You've invested 8.5 hours total. Aim for at least 15-20 minutes per session.",
      "potential_impact": "Medium",
      "estimated_points": 60,
      "action": "Increase time per session to 20-30 minutes"
    }
  ],
  "priority_areas": [
    "Increase activity frequency",
    "Extend session duration"
  ],
  "action_plan": [
    {
      "week": 1,
      "action": "Increase activity frequency to 4+ days per week",
      "goal": "Increase engagement by 75 points",
      "timeframe": "This week"
    }
  ],
  "estimated_improvement": {
    "points": 135,
    "engagement_increase": 15,
    "level_increase": 0,
    "timeframe_days": 14
  }
}
```

---

## ✅ Validation Agent API

### Get Validation Checklist
```http
GET /api/validation/checklist/{challenge_id}
Authorization: Session required

Response:
{
  "status": "success",
  "checklist": {
    "challenge_id": 1,
    "challenge_title": "Daily Grind",
    "checklist": [
      {
        "id": 1,
        "item": "Log in to platform",
        "description": "Successfully log into your account",
        "completed": false,
        "points": 5
      },
      {
        "id": 2,
        "item": "Start one activity",
        "description": "Begin a quiz, study session, or challenge",
        "completed": false,
        "points": 10
      }
    ],
    "total_items": 5,
    "completion_percentage": 0,
    "validation_level": "basic"
  }
}
```

---

## 📈 Diff Viewer API

### Compare Engagement Progress
```http
GET /api/diff/engagement-progress
Authorization: Session required

Response:
{
  "status": "success",
  "diff": {
    "engagement_score": {
      "before": 65.0,
      "after": 75.5,
      "difference": 10.5,
      "percentage_change": 16.2,
      "trend": "up",
      "change_description": "Great progress!",
      "status": "📈"
    },
    "activities_count": {
      "before": 10,
      "after": 12,
      "difference": 2,
      "percentage_change": 20.0,
      "trend": "up",
      "change_description": "Increased",
      "status": "📈"
    },
    "total_time_minutes": {
      "before": 450,
      "after": 480,
      "difference": 30,
      "percentage_change": 6.7,
      "trend": "up",
      "change_description": "Increased",
      "status": "📈"
    },
    "overall_trend": {
      "trend": "upward",
      "sentiment": "Good progress",
      "emoji": "📈",
      "recommendation": "Great momentum! Continue with your current pace."
    },
    "insights": [
      "Engagement improved. Keep this momentum going!",
      "You completed 2 more activities than before.",
      "You spent 30 more minutes learning. Every minute counts!"
    ],
    "visualization": {
      "bar_chart": {
        "labels": ["Engagement Score", "Activities", "Time (hours)"],
        "before": [65.0, 10, 7.5],
        "after": [75.5, 12, 8.0]
      },
      "improvement_percentage": 16.2
    }
  }
}
```

---

## 📝 Activity Logging API

### Log Activity
```http
POST /api/activity/log
Authorization: Session required
Content-Type: application/json

{
  "activity_type": "quiz",
  "activity_name": "Python Basics Quiz",
  "duration_minutes": 30,
  "points_earned": 10,
  "status": "completed",
  "metadata": {
    "score": 85,
    "difficulty": "medium"
  }
}

Response:
{
  "status": "success",
  "message": "Activity logged successfully"
}
```

---

## 🏠 Page Routes

### Public Routes
- `GET /login` - Login page
- `GET /signup` - Signup page
- `GET /` - Redirect to login or dashboard

### Protected Routes (Require Authentication)
- `GET /dashboard` - Main dashboard
- `GET /profile` - User profile
- `GET /leaderboard` - Global leaderboard
- `GET /achievements` - Achievement page
- `GET /logout` - Logout

---

## ⚠️ Error Responses

### 401 Unauthorized
```json
{
  "status": "error",
  "message": "Login required"
}
```

### 404 Not Found
```json
{
  "status": "error",
  "message": "Resource not found"
}
```

### 400 Bad Request
```json
{
  "status": "error",
  "message": "Invalid input parameter"
}
```

### 500 Server Error
```json
{
  "status": "error",
  "message": "Internal server error"
}
```

---

## 📌 Common Parameters

### Activity Types
- `quiz` - Quiz completion
- `challenge` - Challenge completion
- `study` - Study session
- `login` - User login

### Challenge Difficulties
- `easy` - Beginner level
- `medium` - Intermediate level
- `hard` - Advanced level

### Status Values
- `completed` - Successfully completed
- `failed` - Failed attempt
- `pending` - In progress
- `expired` - Time limit expired

### Priority Levels
- `high` - High priority
- `medium` - Medium priority
- `low` - Low priority

---

## 📚 Example Workflows

### Workflow 1: Daily Activity
```
1. User logs in → POST /login
2. Logs activity → POST /api/activity/log
3. Gets rewards → POST /api/rewards/generate
4. Views dashboard → GET /dashboard
5. Logs out → GET /logout
```

### Workflow 2: Challenge Completion
```
1. User generates challenges → POST /api/challenges/generate
2. Views active challenges → GET /api/challenges/active
3. Gets validation checklist → GET /api/validation/checklist/{id}
4. Completes challenge → POST /api/challenges/complete/{id}
5. Gets engagement analysis → POST /api/engagement/analyze
```

### Workflow 3: Progress Tracking
```
1. User gets suggestions → GET /api/optimization/suggest
2. Works on improvements → POST /api/activity/log
3. Compares progress → GET /api/diff/engagement-progress
4. Views updated profile → GET /profile
```

---

## 🔧 Request Examples with cURL

### Login
```bash
curl -c cookies.txt -d "username=testuser&password=pass123" \
  http://localhost:5000/login
```

### Analyze Engagement
```bash
curl -b cookies.txt -X POST \
  http://localhost:5000/api/engagement/analyze
```

### Generate Challenges
```bash
curl -b cookies.txt -X POST \
  http://localhost:5000/api/challenges/generate
```

### Log Activity
```bash
curl -b cookies.txt -X POST \
  -H "Content-Type: application/json" \
  -d '{"activity_type":"quiz","duration_minutes":30,"points_earned":10}' \
  http://localhost:5000/api/activity/log
```

---

## 📊 Rate Limiting (Future)

Recommended implementation:
- 100 requests per minute per user
- 1000 requests per hour per user
- Sliding window algorithm

---

**API Version**: 1.0  
**Last Updated**: 2024  
**Status**: Production Ready ✅
