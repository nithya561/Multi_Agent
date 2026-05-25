"""
Multi-Agent AI Gamified Learning System
Main Flask Application
Orchestrates all agents for user engagement and gamification
"""

import os
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Import agents
from agents.engagement_agent import EngagementAgent
from agents.reward_agent import RewardAgent
from agents.challenge_agent import ChallengeAgent
from agents.optimization_agent import OptimizationAgent
from agents.validation_agent import ValidationAgent
from agents.diff_viewer import DiffViewer

# ============================================================================
# Flask Application Setup
# ============================================================================

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gamified_learning.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ============================================================================
# Database Models
# ============================================================================

class User(db.Model):
    """User model for storing user information"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    activities = db.relationship('UserActivity', backref='user', lazy=True, cascade='all, delete-orphan')
    badges = db.relationship('Badge', secondary='user_badges', backref='users')
    challenges = db.relationship('Challenge', backref='user', lazy=True, cascade='all, delete-orphan')
    rewards = db.relationship('Reward', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password, password)
    
    def get_id(self):
        """Get user id for Flask-Login"""
        return str(self.id)
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def to_dict(self):
        """Convert user to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'points': self.points,
            'level': self.level,
            'current_streak': self.current_streak,
            'longest_streak': self.longest_streak,
            'created_at': self.created_at.isoformat(),
            'badges_count': len(self.badges)
        }


class UserActivity(db.Model):
    """Track user activities for engagement analysis"""
    __tablename__ = 'user_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    activity_type = db.Column(db.String(50), nullable=False)  # quiz, login, study, challenge
    activity_name = db.Column(db.String(255))
    duration_minutes = db.Column(db.Integer, default=0)
    points_earned = db.Column(db.Integer, default=0)
    status = db.Column(db.String(20), default='completed')  # completed, failed, pending
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    metadata_ = db.Column(db.JSON)  # Store additional data
    
    def to_dict(self):
        return {
            'id': self.id,
            'activity_type': self.activity_type,
            'activity_name': self.activity_name,
            'duration_minutes': self.duration_minutes,
            'points_earned': self.points_earned,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class Badge(db.Model):
    """Achievement badges for users"""
    __tablename__ = 'badges'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    icon = db.Column(db.String(255))  # Icon class or image path
    requirement_type = db.Column(db.String(50))  # points, streak, challenges, etc.
    requirement_value = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# Association table for user-badge relationship
user_badges = db.Table('user_badges',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('badge_id', db.Integer, db.ForeignKey('badges.id'), primary_key=True),
    db.Column('earned_at', db.DateTime, default=datetime.utcnow)
)


class Challenge(db.Model):
    """Personalized challenges for users"""
    __tablename__ = 'challenges'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    difficulty_level = db.Column(db.String(20))  # easy, medium, hard
    points_reward = db.Column(db.Integer, default=10)
    status = db.Column(db.String(20), default='active')  # active, completed, failed, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    due_date = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    validation_data = db.Column(db.JSON)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'difficulty_level': self.difficulty_level,
            'points_reward': self.points_reward,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'due_date': self.due_date.isoformat() if self.due_date else None
        }


class Reward(db.Model):
    """Rewards earned by users"""
    __tablename__ = 'rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    reward_type = db.Column(db.String(50))  # points, badge, streak_bonus, etc.
    amount = db.Column(db.Integer)
    reason = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)


class EngagementMetric(db.Model):
    """Historical engagement metrics for comparison"""
    __tablename__ = 'engagement_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    engagement_score = db.Column(db.Float, default=0)
    activities_count = db.Column(db.Integer, default=0)
    total_time_minutes = db.Column(db.Integer, default=0)
    daily_active = db.Column(db.Boolean, default=False)
    recorded_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    metric_data = db.Column(db.JSON)  # Store detailed metrics
    
    def to_dict(self):
        return {
            'engagement_score': self.engagement_score,
            'activities_count': self.activities_count,
            'total_time_minutes': self.total_time_minutes,
            'recorded_at': self.recorded_at.isoformat()
        }


# ============================================================================
# Login Manager Setup
# ============================================================================

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))


# ============================================================================
# Initialize Agents
# ============================================================================

engagement_agent = EngagementAgent()
reward_agent = RewardAgent()
challenge_agent = ChallengeAgent()
optimization_agent = OptimizationAgent()
validation_agent = ValidationAgent()
diff_viewer = DiffViewer()


# ============================================================================
# Routes: Authentication
# ============================================================================

@app.route('/')
def index():
    """Home page"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.session.commit()
            login_user(user, remember=True)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('login.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """User signup"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not username or not email or not password:
            flash('All fields are required', 'error')
            return render_template('signup.html')
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return render_template('signup.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'error')
            return render_template('signup.html')
        
        # Create new user
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')


@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    return redirect(url_for('login'))


# ============================================================================
# Routes: Dashboard and Main Pages
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    user_stats = {
        'points': current_user.points,
        'level': current_user.level,
        'streak': current_user.current_streak,
        'badges': len(current_user.badges),
        'activities_this_week': len(UserActivity.query.filter(
            UserActivity.user_id == current_user.id,
            UserActivity.created_at >= datetime.utcnow() - timedelta(days=7)
        ).all())
    }
    
    # Get recent activities
    recent_activities = UserActivity.query.filter_by(user_id=current_user.id)\
        .order_by(UserActivity.created_at.desc()).limit(10).all()
    
    # Get active challenges
    active_challenges = Challenge.query.filter_by(user_id=current_user.id, status='active')\
        .order_by(Challenge.due_date).limit(5).all()
    
    return render_template('dashboard.html', 
                         user_stats=user_stats,
                         recent_activities=recent_activities,
                         active_challenges=active_challenges)


@app.route('/profile')
@login_required
def profile():
    """User profile page"""
    badges = current_user.badges
    total_points = current_user.points
    level = current_user.level
    
    return render_template('profile.html', 
                         badges=badges,
                         total_points=total_points,
                         level=level)


@app.route('/leaderboard')
@login_required
def leaderboard():
    """Global leaderboard"""
    top_users = User.query.order_by(User.points.desc()).limit(50).all()
    user_rank = db.session.query(db.func.count(User.id))\
        .filter(User.points > current_user.points).scalar() + 1
    
    return render_template('leaderboard.html',
                         top_users=top_users,
                         user_rank=user_rank,
                         current_user=current_user)


@app.route('/achievements')
@login_required
def achievements():
    """Achievement page"""
    all_badges = Badge.query.all()
    user_badges = current_user.badges
    
    return render_template('achievements.html',
                         user_badges=user_badges,
                         all_badges=all_badges)


# ============================================================================
# API Routes: Engagement Agent
# ============================================================================

@app.route('/api/engagement/analyze', methods=['POST'])
@login_required
def api_analyze_engagement():
    """Analyze user engagement"""
    try:
        # Get user activities
        activities = UserActivity.query.filter_by(user_id=current_user.id).all()
        
        # Analyze engagement
        engagement_data = engagement_agent.analyze_engagement(current_user.to_dict(), activities)
        
        # Record metric
        metric = EngagementMetric(
            user_id=current_user.id,
            engagement_score=engagement_data['engagement_score'],
            activities_count=engagement_data['activities_count'],
            total_time_minutes=engagement_data['total_time_minutes'],
            daily_active=engagement_data['daily_active'],
            metric_data=engagement_data
        )
        db.session.add(metric)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'data': engagement_data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/engagement/score', methods=['GET'])
@login_required
def api_engagement_score():
    """Get current engagement score"""
    try:
        activities = UserActivity.query.filter_by(user_id=current_user.id).all()
        score = engagement_agent.calculate_engagement_score(activities)
        
        return jsonify({
            'status': 'success',
            'engagement_score': score
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# API Routes: Reward Agent
# ============================================================================

@app.route('/api/rewards/generate', methods=['POST'])
@login_required
def api_generate_rewards():
    """Generate rewards for user"""
    try:
        data = request.get_json()
        activity_type = data.get('activity_type', 'general')
        points_earned = data.get('points_earned', 10)
        
        # Generate rewards
        rewards = reward_agent.generate_rewards(
            current_user.to_dict(),
            activity_type,
            points_earned
        )
        
        # Apply rewards
        for reward in rewards['rewards']:
            if reward['type'] == 'points':
                current_user.points += reward['amount']
            elif reward['type'] == 'badge':
                # Check and award badge
                badge = Badge.query.filter_by(name=reward['name']).first()
                if badge and badge not in current_user.badges:
                    current_user.badges.append(badge)
        
        # Record reward in database
        reward_record = Reward(
            user_id=current_user.id,
            reward_type=rewards['total_reward_type'],
            amount=rewards['total_points'],
            reason=activity_type
        )
        db.session.add(reward_record)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'rewards': rewards,
            'new_balance': current_user.points
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/rewards/history', methods=['GET'])
@login_required
def api_reward_history():
    """Get reward history"""
    rewards = Reward.query.filter_by(user_id=current_user.id)\
        .order_by(Reward.created_at.desc()).limit(20).all()
    
    return jsonify({
        'status': 'success',
        'rewards': [{
            'id': r.id,
            'type': r.reward_type,
            'amount': r.amount,
            'reason': r.reason,
            'created_at': r.created_at.isoformat()
        } for r in rewards]
    })


# ============================================================================
# API Routes: Challenge Agent
# ============================================================================

@app.route('/api/challenges/generate', methods=['POST'])
@login_required
def api_generate_challenges():
    """Generate personalized challenges"""
    try:
        # Get user activities and engagement data
        activities = UserActivity.query.filter_by(user_id=current_user.id).all()
        engagement_score = engagement_agent.calculate_engagement_score(activities)
        
        # Generate challenges
        challenges_data = challenge_agent.generate_challenges(
            current_user.to_dict(),
            engagement_score,
            activities
        )
        
        # Create challenge records
        for challenge_info in challenges_data['challenges']:
            challenge = Challenge(
                user_id=current_user.id,
                title=challenge_info['title'],
                description=challenge_info['description'],
                difficulty_level=challenge_info['difficulty'],
                points_reward=challenge_info['points'],
                due_date=datetime.utcnow() + timedelta(days=challenge_info['days_to_complete'])
            )
            db.session.add(challenge)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'challenges': challenges_data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/challenges/active', methods=['GET'])
@login_required
def api_get_active_challenges():
    """Get active challenges"""
    challenges = Challenge.query.filter_by(user_id=current_user.id, status='active')\
        .order_by(Challenge.due_date).all()
    
    return jsonify({
        'status': 'success',
        'challenges': [c.to_dict() for c in challenges]
    })


@app.route('/api/challenges/complete/<int:challenge_id>', methods=['POST'])
@login_required
def api_complete_challenge(challenge_id):
    """Mark challenge as completed"""
    try:
        challenge = Challenge.query.filter_by(id=challenge_id, user_id=current_user.id).first()
        
        if not challenge:
            return jsonify({'status': 'error', 'message': 'Challenge not found'}), 404
        
        challenge.status = 'completed'
        challenge.completed_at = datetime.utcnow()
        
        # Award points
        current_user.points += challenge.points_reward
        
        # Record activity
        activity = UserActivity(
            user_id=current_user.id,
            activity_type='challenge',
            activity_name=challenge.title,
            points_earned=challenge.points_reward,
            status='completed'
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': f'Challenge completed! You earned {challenge.points_reward} points',
            'new_balance': current_user.points
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# API Routes: Optimization Agent
# ============================================================================

@app.route('/api/optimization/suggest', methods=['GET'])
@login_required
def api_get_optimization_suggestions():
    """Get optimization suggestions"""
    try:
        # Get user data
        activities = UserActivity.query.filter_by(user_id=current_user.id).all()
        metrics = EngagementMetric.query.filter_by(user_id=current_user.id).all()
        challenges = Challenge.query.filter_by(user_id=current_user.id).all()
        
        # Generate suggestions
        suggestions = optimization_agent.suggest_optimizations(
            current_user.to_dict(),
            activities,
            metrics,
            challenges
        )
        
        return jsonify({
            'status': 'success',
            'suggestions': suggestions
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# API Routes: Validation Agent
# ============================================================================

@app.route('/api/validation/checklist/<int:challenge_id>', methods=['GET'])
@login_required
def api_get_validation_checklist(challenge_id):
    """Get validation checklist for a challenge"""
    try:
        challenge = Challenge.query.filter_by(id=challenge_id, user_id=current_user.id).first()
        
        if not challenge:
            return jsonify({'status': 'error', 'message': 'Challenge not found'}), 404
        
        checklist = validation_agent.get_validation_checklist(challenge.to_dict())
        
        return jsonify({
            'status': 'success',
            'checklist': checklist
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# API Routes: Diff Viewer
# ============================================================================

@app.route('/api/diff/engagement-progress', methods=['GET'])
@login_required
def api_engagement_progress_diff():
    """Get engagement progress diff"""
    try:
        # Get metrics from last 2 periods
        metrics = EngagementMetric.query.filter_by(user_id=current_user.id)\
            .order_by(EngagementMetric.recorded_at.desc()).limit(2).all()
        
        if len(metrics) < 2:
            return jsonify({
                'status': 'error',
                'message': 'Not enough data for comparison'
            }), 400
        
        diff = diff_viewer.compare_metrics(metrics[1].to_dict(), metrics[0].to_dict())
        
        return jsonify({
            'status': 'success',
            'diff': diff
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# API Routes: Activity Tracking
# ============================================================================

@app.route('/api/activity/log', methods=['POST'])
@login_required
def api_log_activity():
    """Log user activity"""
    try:
        data = request.get_json()
        
        activity = UserActivity(
            user_id=current_user.id,
            activity_type=data.get('activity_type', 'general'),
            activity_name=data.get('activity_name'),
            duration_minutes=data.get('duration_minutes', 0),
            points_earned=data.get('points_earned', 0),
            status=data.get('status', 'completed'),
            metadata=data.get('metadata')
        )
        
        db.session.add(activity)
        
        # Update user's streak
        today_activities = UserActivity.query.filter(
            UserActivity.user_id == current_user.id,
            UserActivity.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        ).all()
        
        if len(today_activities) == 1:  # First activity today
            current_user.current_streak += 1
            if current_user.current_streak > current_user.longest_streak:
                current_user.longest_streak = current_user.current_streak
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Activity logged successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('500.html'), 500


# ============================================================================
# Database Initialization
# ============================================================================

def init_db():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Create sample badges
        badges_data = [
            {'name': 'First Step', 'description': 'Complete your first activity', 'requirement_type': 'activities', 'requirement_value': 1},
            {'name': 'Early Bird', 'description': 'Login 7 days in a row', 'requirement_type': 'streak', 'requirement_value': 7},
            {'name': 'Century Club', 'description': 'Earn 100 points', 'requirement_type': 'points', 'requirement_value': 100},
            {'name': 'Quiz Master', 'description': 'Complete 10 quizzes', 'requirement_type': 'quizzes', 'requirement_value': 10},
            {'name': 'Challenge Accepted', 'description': 'Complete 5 challenges', 'requirement_type': 'challenges', 'requirement_value': 5},
        ]
        
        for badge_data in badges_data:
            if not Badge.query.filter_by(name=badge_data['name']).first():
                badge = Badge(**badge_data)
                db.session.add(badge)
        
        db.session.commit()
        print("Database initialized successfully!")


# ============================================================================
# Main Entry Point
# ============================================================================

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
