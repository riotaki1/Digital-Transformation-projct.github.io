from flask import Flask, request, jsonify, session
import json
import random
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'career_autopilot_secret_key'

# Mock data for demonstration
CAREER_PATHS = {
    "Data Scientist": {
        "skills": ["Python", "SQL", "Machine Learning", "Statistics", "Data Visualization"],
        "description": "Specialist in data analysis and building ML models"
    },
    "Frontend Developer": {
        "skills": ["JavaScript", "React", "HTML/CSS", "TypeScript", "UI/UX"],
        "description": "User interface developer"
    },
    "Project Manager": {
        "skills": ["Project Management", "Communication", "Agile", "Presentations", "Leadership"],
        "description": "Project and team leader"
    }
}

QUESTS = [
    {"id": 1, "name": "Complete a Python course", "xp": 100, "coins": 50, "skill": "Python", "type": "education"},
    {"id": 2, "name": "Watch an Agile webinar", "xp": 80, "coins": 40, "skill": "Agile", "type": "education"},
    {"id": 3, "name": "Read an article about React", "xp": 60, "coins": 30, "skill": "React", "type": "reading"},
    {"id": 4, "name": "Ask for feedback from a colleague", "xp": 120, "coins": 60, "skill": "Communication", "type": "social"},
    {"id": 5, "name": "Solve an algorithms problem", "xp": 150, "coins": 75, "skill": "Python", "type": "practice"},
    {"id": 6, "name": "Prepare a presentation", "xp": 90, "coins": 45, "skill": "Presentations", "type": "practice"}
]

BADGES = {
    "python_beginner": {"name": "Python Beginner", "description": "Completed first Python task", "icon": "🐍"},
    "active_learner": {"name": "Active Learner", "description": "Completed 5 tasks", "icon": "⭐"},
    "team_player": {"name": "Team Player", "description": "Received feedback from a colleague", "icon": "👥"},
    "ml_master": {"name": "ML Master", "description": "Mastered machine learning", "icon": "🤖"},
    "quest_master": {"name": "Quest Master", "description": "Completed 10 tasks", "icon": "🏆"},
    "skill_collector": {"name": "Skill Collector", "description": "Learned 5 different skills", "icon": "📚"}
}

# Predefined goals for selection
CAREER_GOALS = {
    "short_term": [
        {"id": 1, "name": "Learn basic Python syntax", "category": "Programming", "priority": "high"},
        {"id": 2, "name": "Study SQL fundamentals", "category": "Databases", "priority": "medium"},
        {"id": 3, "name": "Understand OOP principles", "category": "Programming", "priority": "high"},
        {"id": 4, "name": "Learn to work with Git", "category": "Tools", "priority": "medium"},
        {"id": 5, "name": "Master algorithm basics", "category": "Programming", "priority": "medium"}
    ],
    "medium_term": [
        {"id": 6, "name": "Develop your own project", "category": "Practice", "priority": "high"},
        {"id": 7, "name": "Learn Django/Flask framework", "category": "Programming", "priority": "medium"},
        {"id": 8, "name": "Master machine learning basics", "category": "Data Science", "priority": "medium"},
        {"id": 9, "name": "Learn to work with Docker", "category": "Infrastructure", "priority": "low"},
        {"id": 10, "name": "Study web development basics", "category": "Web", "priority": "medium"}
    ],
    "long_term": [
        {"id": 11, "name": "Become a Middle Developer", "category": "Career", "priority": "high"},
        {"id": 12, "name": "Participate in open-source project", "category": "Practice", "priority": "medium"},
        {"id": 13, "name": "Prepare for technical interview", "category": "Career", "priority": "high"},
        {"id": 14, "name": "Master advanced algorithms", "category": "Programming", "priority": "medium"},
        {"id": 15, "name": "Study application architecture", "category": "Architecture", "priority": "medium"}
    ]
}

# Predefined AI assistant responses
AI_RESPONSES = {
    "hello": "Hello! I'm your AI career assistant. How can I help with your professional development?",
    "hi": "Hi! I'm your AI career assistant. How can I help with your professional development?",
    "how are you": "Everything is great! Ready to help you with career questions and skill development.",
    "what can you do": "I can help with career path selection, recommend skill development tasks, track progress and set goals.",
    "career": "Analyzing your profile, I see potential in Data Science. I recommend starting with Python basics and statistics.",
    "skills": "Your current skills: Python (65%), SQL (40%). For your chosen path, I recommend learning machine learning and data visualization.",
    "plan": "Your career plan:\n1. Master Python (2 weeks)\n2. Learn SQL (3 weeks)\n3. ML basics (4 weeks)\n4. Real projects (2 months)",
    "quests": "Today available quests: Python, Agile and teamwork. Choose what aligns with your goals!",
    "statistics": "Check the 'Personal Account' section to view your detailed statistics and skill progress.",
    "goals": "In your personal account, you can select and track your career goals. I'll help choose suitable goals for your development.",
    "default": "I'm here to help with your career development. Ask about skills, career plan, available tasks or recommendations."
}


def get_user_data():
    if 'user_data' not in session:
        session['user_data'] = {
            'level': 1,
            'xp': 0,
            'coins': 0,
            'badges': [],
            'completed_quests': [],
            'career_path': None,
            'skills_progress': {
                "Python": 65,
                "SQL": 40,
                "Machine Learning": 20,
                "Statistics": 30,
                "Data Visualization": 25,
                "JavaScript": 10,
                "React": 5,
                "HTML/CSS": 15,
                "TypeScript": 0,
                "UI/UX": 10,
                "Project Management": 35,
                "Communication": 60,
                "Agile": 45,
                "Presentations": 50,
                "Leadership": 40
            },
            'join_date': datetime.now().strftime("%m/%d/%Y"),
            'total_quests_completed': 0,
            'total_xp_earned': 0,
            'total_coins_earned': 0,
            'quests_by_type': {
                'education': 0,
                'reading': 0,
                'social': 0,
                'practice': 0
            },
            'last_activity': datetime.now().strftime("%m/%d/%Y %H:%M"),
            'learning_streak': 1,
            'career_goals': {
                'short_term': [],
                'medium_term': [],
                'long_term': []
            }
        }
    return session['user_data']


def update_skills_progress(user_data, skill, xp_earned):
    """Update skill progress based on earned experience"""
    if skill in user_data['skills_progress']:
        progress_increase = min(xp_earned / 10, 10)
        user_data['skills_progress'][skill] = min(
            user_data['skills_progress'][skill] + progress_increase,
            100
        )
    else:
        user_data['skills_progress'][skill] = min(xp_earned / 5, 20)


def ai_assistant_response(message):
    """Simplified AI assistant with predefined responses"""
    message_lower = message.lower()

    # Search for keywords in the message
    for key, response in AI_RESPONSES.items():
        if key in message_lower and key != "default":
            return response

    # If no keywords found, return default response
    return AI_RESPONSES["default"]


@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Internal Growth | Holding T1</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {
                --primary-blue: #4a90e2;
                --light-blue: #87ceeb;
                --soft-blue: #b0e0e6;
                --very-light-blue: #e6f3ff;
                --dark-blue: #2c5aa0;
                --text-dark: #2c3e50;
                --text-light: #7f8c8d;
                --white: #ffffff;
                --success: #27ae60;
                --warning: #f39c12;
                --danger: #e74c3c;
            }

            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }

            body {
                background: linear-gradient(135deg, var(--very-light-blue) 0%, var(--soft-blue) 100%);
                color: var(--text-dark);
                min-height: 100vh;
            }

            .app-container {
                display: flex;
                min-height: 100vh;
            }

            /* Sidebar */
            .sidebar {
                width: 280px;
                background: linear-gradient(180deg, var(--primary-blue) 0%, var(--dark-blue) 100%);
                color: white;
                padding: 20px;
                box-shadow: 2px 0 10px rgba(0,0,0,0.1);
                display: flex;
                flex-direction: column;
            }

            .logo {
                display: flex;
                align-items: center;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid rgba(255,255,255,0.2);
            }

            .logo i {
                font-size: 24px;
                margin-right: 10px;
            }

            .logo h1 {
                font-size: 18px;
                font-weight: 600;
            }

            .user-profile {
                text-align: center;
                margin-bottom: 30px;
            }

            .avatar {
                width: 80px;
                height: 80px;
                border-radius: 50%;
                background: rgba(255,255,255,0.2);
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 0 auto 15px;
                font-size: 32px;
            }

            .user-level {
                background: rgba(255,255,255,0.2);
                border-radius: 20px;
                padding: 5px 15px;
                display: inline-block;
                font-size: 14px;
                margin-bottom: 10px;
            }

            .progress-container {
                margin: 15px 0;
            }

            .progress-bar {
                height: 8px;
                background: rgba(255,255,255,0.2);
                border-radius: 4px;
                overflow: hidden;
            }

            .progress-fill {
                height: 100%;
                background: var(--light-blue);
                border-radius: 4px;
                transition: width 0.3s ease;
            }

            .stats {
                display: flex;
                justify-content: space-around;
                margin: 20px 0;
            }

            .stat-item {
                text-align: center;
            }

            .stat-value {
                font-size: 20px;
                font-weight: bold;
            }

            .stat-label {
                font-size: 12px;
                opacity: 0.8;
            }

            .nav-menu {
                flex-grow: 1;
            }

            .nav-item {
                padding: 12px 15px;
                border-radius: 8px;
                margin-bottom: 8px;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
            }

            .nav-item:hover, .nav-item.active {
                background: rgba(255,255,255,0.15);
            }

            .nav-item i {
                margin-right: 10px;
                width: 20px;
                text-align: center;
            }

            /* Main content */
            .main-content {
                flex-grow: 1;
                padding: 30px;
                overflow-y: auto;
            }

            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 30px;
            }

            .header h2 {
                font-size: 28px;
                color: var(--dark-blue);
                font-weight: 600;
            }

            .date-display {
                color: var(--text-light);
                font-size: 14px;
            }

            .content-section {
                display: none;
            }

            .content-section.active {
                display: block;
            }

            .section-title {
                font-size: 22px;
                margin-bottom: 20px;
                color: var(--dark-blue);
                display: flex;
                align-items: center;
            }

            .section-title i {
                margin-right: 10px;
            }

            /* Cards */
            .cards-container {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }

            .card {
                background: var(--white);
                border-radius: 12px;
                padding: 20px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }

            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            }

            .card-title {
                font-size: 18px;
                margin-bottom: 15px;
                color: var(--dark-blue);
                display: flex;
                align-items: center;
            }

            .card-title i {
                margin-right: 10px;
                color: var(--primary-blue);
            }

            /* Quests */
            .quest-item {
                background: var(--white);
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 15px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            }

            .quest-info {
                flex-grow: 1;
            }

            .quest-name {
                font-weight: 600;
                margin-bottom: 5px;
            }

            .quest-meta {
                display: flex;
                font-size: 14px;
                color: var(--text-light);
            }

            .quest-meta span {
                margin-right: 15px;
                display: flex;
                align-items: center;
            }

            .quest-meta i {
                margin-right: 5px;
            }

            .quest-type {
                background: var(--soft-blue);
                color: var(--dark-blue);
                padding: 3px 8px;
                border-radius: 20px;
                font-size: 12px;
                margin-top: 5px;
                display: inline-block;
            }

            .btn {
                background: var(--primary-blue);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                cursor: pointer;
                transition: background 0.3s ease;
                font-weight: 500;
            }

            .btn:hover {
                background: var(--dark-blue);
            }

            .btn:disabled {
                background: var(--text-light);
                cursor: not-allowed;
            }

            .btn-success {
                background: var(--success);
            }

            .btn-success:hover {
                background: #219653;
            }

            .btn-warning {
                background: var(--warning);
            }

            .btn-warning:hover {
                background: #e67e22;
            }

            .btn-danger {
                background: var(--danger);
            }

            .btn-danger:hover {
                background: #c0392b;
            }

            /* AI Chat */
            .chat-container {
                background: var(--white);
                border-radius: 12px;
                overflow: hidden;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                height: 500px;
                display: flex;
                flex-direction: column;
            }

            .chat-messages {
                flex-grow: 1;
                padding: 20px;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
            }

            .message {
                max-width: 80%;
                padding: 12px 16px;
                border-radius: 18px;
                margin-bottom: 15px;
                line-height: 1.4;
            }

            .user-message {
                align-self: flex-end;
                background: var(--primary-blue);
                color: white;
                border-bottom-right-radius: 4px;
            }

            .ai-message {
                align-self: flex-start;
                background: var(--very-light-blue);
                color: var(--text-dark);
                border-bottom-left-radius: 4px;
            }

            .chat-input {
                display: flex;
                padding: 15px;
                border-top: 1px solid #eee;
            }

            .chat-input input {
                flex-grow: 1;
                padding: 12px 15px;
                border: 1px solid #ddd;
                border-radius: 24px;
                margin-right: 10px;
                outline: none;
                transition: border 0.3s ease;
            }

            .chat-input input:focus {
                border-color: var(--primary-blue);
            }

            .chat-input button {
                background: var(--primary-blue);
                color: white;
                border: none;
                border-radius: 50%;
                width: 44px;
                height: 44px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                transition: background 0.3s ease;
            }

            .chat-input button:hover {
                background: var(--dark-blue);
            }

            /* Career paths */
            .career-path {
                background: var(--white);
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                cursor: pointer;
                transition: all 0.3s ease;
                border: 2px solid transparent;
            }

            .career-path:hover {
                border-color: var(--primary-blue);
            }

            .career-path.selected {
                border-color: var(--primary-blue);
                background: var(--very-light-blue);
            }

            .career-title {
                font-size: 20px;
                margin-bottom: 10px;
                color: var(--dark-blue);
            }

            .career-description {
                color: var(--text-light);
                margin-bottom: 15px;
            }

            .skills-list {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
            }

            .skill-tag {
                background: var(--soft-blue);
                color: var(--dark-blue);
                padding: 5px 10px;
                border-radius: 20px;
                font-size: 14px;
            }

            /* Badges */
            .badges-container {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 20px;
            }

            .badge {
                background: var(--white);
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                transition: transform 0.3s ease;
            }

            .badge:hover {
                transform: translateY(-5px);
            }

            .badge-icon {
                font-size: 40px;
                margin-bottom: 15px;
            }

            .badge-name {
                font-weight: 600;
                margin-bottom: 10px;
                color: var(--dark-blue);
            }

            .badge-description {
                color: var(--text-light);
                font-size: 14px;
            }

            .badge.locked {
                opacity: 0.5;
            }

            /* Personal Account */
            .profile-header {
                display: flex;
                align-items: center;
                margin-bottom: 30px;
                background: var(--white);
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            }

            .profile-avatar {
                width: 100px;
                height: 100px;
                border-radius: 50%;
                background: var(--primary-blue);
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 25px;
                font-size: 40px;
                color: white;
            }

            .profile-info h3 {
                font-size: 24px;
                margin-bottom: 5px;
                color: var(--dark-blue);
            }

            .profile-info p {
                color: var(--text-light);
                margin-bottom: 10px;
            }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }

            .stat-card {
                background: var(--white);
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            }

            .stat-card i {
                font-size: 30px;
                color: var(--primary-blue);
                margin-bottom: 15px;
            }

            .stat-card-value {
                font-size: 28px;
                font-weight: bold;
                margin-bottom: 5px;
                color: var(--dark-blue);
            }

            .stat-card-label {
                color: var(--text-light);
                font-size: 14px;
            }

            .skills-progress {
                background: var(--white);
                border-radius: 12px;
                padding: 25px;
                margin-bottom: 30px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
            }

            .skill-item {
                margin-bottom: 15px;
            }

            .skill-header {
                display: flex;
                justify-content: space-between;
                margin-bottom: 8px;
            }

            .skill-name {
                font-weight: 500;
            }

            .skill-percent {
                color: var(--text-light);
            }

            .skill-progress-bar {
                height: 10px;
                background: #f0f0f0;
                border-radius: 5px;
                overflow: hidden;
            }

            .skill-progress-fill {
                height: 100%;
                background: var(--primary-blue);
                border-radius: 5px;
                transition: width 0.5s ease;
            }

            .quests-stats {
                background: var(--white);
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                margin-bottom: 30px;
            }

            .quest-type-stats {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }

            .quest-type-stat {
                text-align: center;
                padding: 15px;
                background: var(--very-light-blue);
                border-radius: 8px;
            }

            .quest-type-stat i {
                font-size: 24px;
                color: var(--primary-blue);
                margin-bottom: 10px;
            }

            .quest-type-count {
                font-size: 20px;
                font-weight: bold;
                color: var(--dark-blue);
            }

            .quest-type-label {
                font-size: 14px;
                color: var(--text-light);
            }

            /* Goals */
            .goals-section {
                background: var(--white);
                border-radius: 12px;
                padding: 25px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                margin-bottom: 30px;
            }

            .goals-tabs {
                display: flex;
                margin-bottom: 20px;
                border-bottom: 1px solid #eee;
            }

            .goal-tab {
                padding: 10px 20px;
                cursor: pointer;
                border-bottom: 3px solid transparent;
                transition: all 0.3s ease;
            }

            .goal-tab.active {
                border-bottom-color: var(--primary-blue);
                color: var(--primary-blue);
                font-weight: 500;
            }

            .goal-tab:hover {
                color: var(--primary-blue);
            }

            .goals-list {
                display: none;
            }

            .goals-list.active {
                display: block;
            }

            .goal-item {
                display: flex;
                align-items: center;
                padding: 15px;
                border: 1px solid #eee;
                border-radius: 8px;
                margin-bottom: 10px;
                transition: all 0.3s ease;
            }

            .goal-item:hover {
                border-color: var(--primary-blue);
                background: var(--very-light-blue);
            }

            .goal-item.completed {
                background: #f0fff4;
                border-color: var(--success);
            }

            .goal-checkbox {
                margin-right: 15px;
                width: 20px;
                height: 20px;
                cursor: pointer;
            }

            .goal-content {
                flex-grow: 1;
            }

            .goal-name {
                font-weight: 500;
                margin-bottom: 5px;
            }

            .goal-meta {
                display: flex;
                font-size: 14px;
                color: var(--text-light);
            }

            .goal-category, .goal-priority {
                margin-right: 15px;
                display: flex;
                align-items: center;
            }

            .goal-priority.high::before {
                content: "";
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: var(--danger);
                margin-right: 5px;
            }

            .goal-priority.medium::before {
                content: "";
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: var(--warning);
                margin-right: 5px;
            }

            .goal-priority.low::before {
                content: "";
                display: inline-block;
                width: 8px;
                height: 8px;
                border-radius: 50%;
                background: var(--success);
                margin-right: 5px;
            }

            .goal-actions {
                display: flex;
                gap: 10px;
            }

            .available-goals {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 15px;
            }

            .available-goal {
                background: var(--white);
                border: 1px solid #eee;
                border-radius: 8px;
                padding: 15px;
                transition: all 0.3s ease;
                cursor: pointer;
            }

            .available-goal:hover {
                border-color: var(--primary-blue);
                transform: translateY(-2px);
            }

            .available-goal.selected {
                border-color: var(--primary-blue);
                background: var(--very-light-blue);
            }

            /* Responsive */
            @media (max-width: 768px) {
                .app-container {
                    flex-direction: column;
                }
                .sidebar {
                    width: 100%;
                    height: auto;
                }
                .cards-container {
                    grid-template-columns: 1fr;
                }
                .profile-header {
                    flex-direction: column;
                    text-align: center;
                }
                .profile-avatar {
                    margin-right: 0;
                    margin-bottom: 15px;
                }
                .goal-item {
                    flex-direction: column;
                    align-items: flex-start;
                }
                .goal-actions {
                    margin-top: 10px;
                    width: 100%;
                    justify-content: flex-end;
                }
            }
        </style>
    </head>
    <body>
        <div class="app-container">
            <!-- Sidebar -->
            <div class="sidebar">
                <div class="logo">
                    <i class="fas fa-rocket"></i>
                    <h1>Internal Growth</h1>
                </div>

                <div class="user-profile">
                    <div class="avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="user-level">Level <span id="user-level">1</span></div>
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div class="progress-fill" id="xp-progress" style="width: 0%"></div>
                        </div>
                    </div>
                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-value" id="user-xp">0</div>
                            <div class="stat-label">XP</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="user-coins">0</div>
                            <div class="stat-label">Coins</div>
                        </div>
                    </div>
                </div>

                <div class="nav-menu">
                    <div class="nav-item active" data-section="dashboard">
                        <i class="fas fa-home"></i>
                        <span>Dashboard</span>
                    </div>
                    <div class="nav-item" data-section="career">
                        <i class="fas fa-map"></i>
                        <span>Career Map</span>
                    </div>
                    <div class="nav-item" data-section="quests">
                        <i class="fas fa-tasks"></i>
                        <span>Quests</span>
                    </div>
                    <div class="nav-item" data-section="ai">
                        <i class="fas fa-robot"></i>
                        <span>AI Assistant</span>
                    </div>
                    <div class="nav-item" data-section="achievements">
                        <i class="fas fa-trophy"></i>
                        <span>Achievements</span>
                    </div>
                    <div class="nav-item" data-section="profile">
                        <i class="fas fa-user-circle"></i>
                        <span>Personal Account</span>
                    </div>
                </div>

                <div class="footer">
                    <div class="company">Holding T1</div>
                </div>
            </div>

            <!-- Main Content -->
            <div class="main-content">
                <div class="header">
                    <h2 id="page-title">Dashboard</h2>
                    <div class="date-display" id="current-date"></div>
                </div>

                <!-- Dashboard -->
                <div class="content-section active" id="dashboard">
                    <div class="section-title">
                        <i class="fas fa-tachometer-alt"></i>
                        <span>Progress Overview</span>
                    </div>

                    <div class="cards-container">
                        <div class="card">
                            <div class="card-title">
                                <i class="fas fa-chart-line"></i>
                                <span>Your Progress</span>
                            </div>
                            <div id="progress-stats">
                                Loading...
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-title">
                                <i class="fas fa-star"></i>
                                <span>Next Goals</span>
                            </div>
                            <div id="next-goals">
                                Loading...
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-title">
                                <i class="fas fa-bullseye"></i>
                                <span>Active Quests</span>
                            </div>
                            <div id="active-quests">
                                Loading...
                            </div>
                        </div>
                    </div>

                    <div class="section-title">
                        <i class="fas fa-road"></i>
                        <span>Your Career Path</span>
                    </div>

                    <div id="user-career-path">
                        <p>You haven't chosen a career path yet. Go to the "Career Map" section to select one.</p>
                    </div>
                </div>

                <!-- Career Map -->
                <div class="content-section" id="career">
                    <div class="section-title">
                        <i class="fas fa-map"></i>
                        <span>Choose Your Career Path</span>
                    </div>

                    <p style="margin-bottom: 20px;">Choose the direction you want to develop in. The AI assistant will create a personalized development plan.</p>

                    <div id="career-paths-list">
                        Loading career paths...
                    </div>
                </div>

                <!-- Quests -->
                <div class="content-section" id="quests">
                    <div class="section-title">
                        <i class="fas fa-tasks"></i>
                        <span>Available Quests</span>
                    </div>

                    <p style="margin-bottom: 20px;">Complete tasks to earn experience, coins, and badges.</p>

                    <div id="quests-list">
                        Loading quests...
                    </div>
                </div>

                <!-- AI Assistant -->
                <div class="content-section" id="ai">
                    <div class="section-title">
                        <i class="fas fa-robot"></i>
                        <span>AI Career Assistant</span>
                    </div>

                    <p style="margin-bottom: 20px;">Ask a question about your career development, skills, or available tasks.</p>

                    <div class="chat-container">
                        <div class="chat-messages" id="chat-messages">
                            <div class="message ai-message">
                                Hello! I'm your AI career development assistant. Ask me about your skills, career plan, or available tasks.
                            </div>
                        </div>
                        <div class="chat-input">
                            <input type="text" id="chat-input" placeholder="Enter your question...">
                            <button id="send-message">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Achievements -->
                <div class="content-section" id="achievements">
                    <div class="section-title">
                        <i class="fas fa-trophy"></i>
                        <span>Your Achievements</span>
                    </div>

                    <div class="badges-container" id="badges-container">
                        Loading badges...
                    </div>
                </div>

                <!-- Personal Account -->
                <div class="content-section" id="profile">
                    <div class="section-title">
                        <i class="fas fa-user-circle"></i>
                        <span>Personal Account</span>
                    </div>

                    <div class="profile-header">
                        <div class="profile-avatar">
                            <i class="fas fa-user"></i>
                        </div>
                        <div class="profile-info">
                            <h3 id="profile-username">Holding T1 Employee</h3>
                            <p id="profile-career-path">Career Path: Not selected</p>
                            <p id="profile-join-date">Team member since: Loading...</p>
                            <p id="profile-last-activity">Last activity: Loading...</p>
                        </div>
                    </div>

                    <div class="stats-grid">
                        <div class="stat-card">
                            <i class="fas fa-chart-line"></i>
                            <div class="stat-card-value" id="stat-level">1</div>
                            <div class="stat-card-label">Current Level</div>
                        </div>
                        <div class="stat-card">
                            <i class="fas fa-star"></i>
                            <div class="stat-card-value" id="stat-total-xp">0</div>
                            <div class="stat-card-label">Total XP</div>
                        </div>
                        <div class="stat-card">
                            <i class="fas fa-coins"></i>
                            <div class="stat-card-value" id="stat-total-coins">0</div>
                            <div class="stat-card-label">Total Coins</div>
                        </div>
                        <div class="stat-card">
                            <i class="fas fa-tasks"></i>
                            <div class="stat-card-value" id="stat-total-quests">0</div>
                            <div class="stat-card-label">Quests Completed</div>
                        </div>
                        <div class="stat-card">
                            <i class="fas fa-trophy"></i>
                            <div class="stat-card-value" id="stat-badges">0</div>
                            <div class="stat-card-label">Badges Earned</div>
                        </div>
                        <div class="stat-card">
                            <i class="fas fa-fire"></i>
                            <div class="stat-card-value" id="stat-streak">1</div>
                            <div class="stat-card-label">Day Streak</div>
                        </div>
                    </div>

                    <div class="skills-progress">
                        <h3 style="margin-bottom: 20px; color: var(--dark-blue);">Skills Progress</h3>
                        <div id="skills-progress-list">
                            Loading skills...
                        </div>
                    </div>

                    <div class="quests-stats">
                        <h3 style="margin-bottom: 20px; color: var(--dark-blue);">Quest Statistics</h3>
                        <div class="quest-type-stats" id="quests-type-stats">
                            <!-- Will be filled via JavaScript -->
                        </div>
                    </div>

                    <!-- New section: My Goals -->
                    <div class="goals-section">
                        <h3 style="margin-bottom: 20px; color: var(--dark-blue);">My Career Goals</h3>

                        <div class="goals-tabs">
                            <div class="goal-tab active" data-tab="my-goals">My Goals</div>
                            <div class="goal-tab" data-tab="available-goals">Available Goals</div>
                        </div>

                        <div class="goals-list active" id="my-goals-list">
                            <div id="my-goals-content">
                                Loading your goals...
                            </div>
                        </div>

                        <div class="goals-list" id="available-goals-list">
                            <div class="available-goals" id="available-goals-content">
                                Loading available goals...
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Current user
            let userData = {};

            // Load user data
            async function loadUserData() {
                try {
                    const response = await fetch('/api/user');
                    userData = await response.json();
                    updateUI();
                } catch (error) {
                    console.error('Error loading data:', error);
                }
            }

            // Update interface
            function updateUI() {
                // Update sidebar
                document.getElementById('user-level').textContent = userData.level;
                document.getElementById('user-xp').textContent = userData.xp;
                document.getElementById('user-coins').textContent = userData.coins;

                // Progress bar
                const xpNeeded = userData.level * 100;
                const progressPercent = (userData.xp / xpNeeded) * 100;
                document.getElementById('xp-progress').style.width = `${progressPercent}%`;

                // Update date
                const now = new Date();
                document.getElementById('current-date').textContent = now.toLocaleDateString('en-US', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });

                // Update sections
                updateDashboard();
                updateCareerPaths();
                updateQuests();
                updateBadges();
                updateProfile();
                updateGoals();
            }

            // Update dashboard
            function updateDashboard() {
                // Progress statistics
                document.getElementById('progress-stats').innerHTML = `
                    <p>Level: <strong>${userData.level}</strong></p>
                    <p>XP: <strong>${userData.xp}/${userData.level * 100}</strong></p>
                    <p>Coins: <strong>${userData.coins}</strong></p>
                    <p>Quests completed: <strong>${userData.completed_quests.length}</strong></p>
                `;

                // Next goals
                document.getElementById('next-goals').innerHTML = `
                    <p>• Reach level ${userData.level + 1}</p>
                    <p>• Complete 3 quests for "Active Learner" badge</p>
                    <p>• Learn Python for "Python Beginner" badge</p>
                `;

                // Active quests
                const activeQuestsCount = Math.min(3, 6 - userData.completed_quests.length);
                document.getElementById('active-quests').innerHTML = `
                    <p>You have <strong>${activeQuestsCount}</strong> active quests</p>
                    <p>Go to "Quests" section to view them</p>
                `;

                // Career path
                if (userData.career_path) {
                    document.getElementById('user-career-path').innerHTML = `
                        <div class="career-path selected">
                            <div class="career-title">${userData.career_path}</div>
                            <p>You are actively developing in this direction. Continue completing quests to advance your career!</p>
                        </div>
                    `;
                }
            }

            // Update personal account
            function updateProfile() {
                // Basic information
                document.getElementById('profile-username').textContent = 'Holding T1 Employee';
                document.getElementById('profile-career-path').textContent = 
                    userData.career_path ? `Career Path: ${userData.career_path}` : 'Career Path: Not selected';
                document.getElementById('profile-join-date').textContent = `Team member since: ${userData.join_date}`;
                document.getElementById('profile-last-activity').textContent = `Last activity: ${userData.last_activity}`;

                // Statistics
                document.getElementById('stat-level').textContent = userData.level;
                document.getElementById('stat-total-xp').textContent = userData.total_xp_earned || userData.xp;
                document.getElementById('stat-total-coins').textContent = userData.total_coins_earned || userData.coins;
                document.getElementById('stat-total-quests').textContent = userData.total_quests_completed || userData.completed_quests.length;
                document.getElementById('stat-badges').textContent = userData.badges.length;
                document.getElementById('stat-streak').textContent = userData.learning_streak || 1;

                // Skills progress
                if (userData.skills_progress) {
                    let skillsHTML = '';
                    for (const [skill, progress] of Object.entries(userData.skills_progress)) {
                        skillsHTML += `
                            <div class="skill-item">
                                <div class="skill-header">
                                    <span class="skill-name">${skill}</span>
                                    <span class="skill-percent">${Math.round(progress)}%</span>
                                </div>
                                <div class="skill-progress-bar">
                                    <div class="skill-progress-fill" style="width: ${progress}%"></div>
                                </div>
                            </div>
                        `;
                    }
                    document.getElementById('skills-progress-list').innerHTML = skillsHTML;
                }

                // Quest type statistics
                if (userData.quests_by_type) {
                    const questTypes = {
                        'education': { icon: 'fas fa-graduation-cap', label: 'Education' },
                        'reading': { icon: 'fas fa-book', label: 'Reading' },
                        'social': { icon: 'fas fa-users', label: 'Social' },
                        'practice': { icon: 'fas fa-laptop-code', label: 'Practice' }
                    };

                    let questsStatsHTML = '';
                    for (const [type, data] of Object.entries(questTypes)) {
                        const count = userData.quests_by_type[type] || 0;
                        questsStatsHTML += `
                            <div class="quest-type-stat">
                                <i class="${data.icon}"></i>
                                <div class="quest-type-count">${count}</div>
                                <div class="quest-type-label">${data.label}</div>
                            </div>
                        `;
                    }
                    document.getElementById('quests-type-stats').innerHTML = questsStatsHTML;
                }
            }

            // Update goals
            async function updateGoals() {
                try {
                    // Load available goals
                    const response = await fetch('/api/career_goals');
                    const availableGoals = await response.json();

                    // Display my goals
                    displayMyGoals();

                    // Display available goals
                    displayAvailableGoals(availableGoals);

                } catch (error) {
                    console.error('Error loading goals:', error);
                }
            }

            // Display my goals
            function displayMyGoals() {
                const myGoals = userData.career_goals || {
                    'short_term': [],
                    'medium_term': [],
                    'long_term': []
                };

                let html = '';

                // Short-term goals
                if (myGoals.short_term && myGoals.short_term.length > 0) {
                    html += `<h4 style="margin: 15px 0 10px 0; color: var(--dark-blue);">Short-term Goals</h4>`;
                    myGoals.short_term.forEach(goal => {
                        html += createGoalItem(goal, 'short_term');
                    });
                }

                // Medium-term goals
                if (myGoals.medium_term && myGoals.medium_term.length > 0) {
                    html += `<h4 style="margin: 15px 0 10px 0; color: var(--dark-blue);">Medium-term Goals</h4>`;
                    myGoals.medium_term.forEach(goal => {
                        html += createGoalItem(goal, 'medium_term');
                    });
                }

                // Long-term goals
                if (myGoals.long_term && myGoals.long_term.length > 0) {
                    html += `<h4 style="margin: 15px 0 10px 0; color: var(--dark-blue);">Long-term Goals</h4>`;
                    myGoals.long_term.forEach(goal => {
                        html += createGoalItem(goal, 'long_term');
                    });
                }

                if (!html) {
                    html = '<p>You don\'t have any goals selected yet. Go to the "Available Goals" tab to add goals for tracking.</p>';
                }

                document.getElementById('my-goals-content').innerHTML = html;

                // Add event handlers for checkboxes and delete buttons
                addGoalEventListeners();
            }

            // Create goal item
            function createGoalItem(goal, term) {
                const completedClass = goal.completed ? 'completed' : '';
                return `
                    <div class="goal-item ${completedClass}" data-id="${goal.id}" data-term="${term}">
                        <input type="checkbox" class="goal-checkbox" ${goal.completed ? 'checked' : ''}>
                        <div class="goal-content">
                            <div class="goal-name">${goal.name}</div>
                            <div class="goal-meta">
                                <span class="goal-category">${goal.category}</span>
                                <span class="goal-priority ${goal.priority}">${getPriorityLabel(goal.priority)}</span>
                            </div>
                        </div>
                        <div class="goal-actions">
                            <button class="btn btn-danger remove-goal">Remove</button>
                        </div>
                    </div>
                `;
            }

            // Get priority label text
            function getPriorityLabel(priority) {
                const labels = {
                    'high': 'High',
                    'medium': 'Medium',
                    'low': 'Low'
                };
                return labels[priority] || priority;
            }

            // Display available goals
            function displayAvailableGoals(availableGoals) {
                let html = '';

                // Short-term goals
                html += `<h4 style="margin: 15px 0 10px 0; color: var(--dark-blue);">Short-term Goals</h4>`;
                availableGoals.short_term.forEach(goal => {
                    html += createAvailableGoalItem(goal, 'short_term');
                });

                // Medium-term goals
                html += `<h4 style="margin: 15px 0 10px 0; color: var(--dark-blue);">Medium-term Goals</h4>`;
                availableGoals.medium_term.forEach(goal => {
                    html += createAvailableGoalItem(goal, 'medium_term');
                });

                // Long-term goals
                html += `<h4 style="margin: 15px 0 10px 0; color: var(--dark-blue);">Long-term Goals</h4>`;
                availableGoals.long_term.forEach(goal => {
                    html += createAvailableGoalItem(goal, 'long_term');
                });

                document.getElementById('available-goals-content').innerHTML = html;

                // Add event handlers for goal selection
                addAvailableGoalEventListeners();
            }

            // Create available goal item
            function createAvailableGoalItem(goal, term) {
                // Check if goal is already added
                const myGoals = userData.career_goals || {
                    'short_term': [],
                    'medium_term': [],
                    'long_term': []
                };

                const isAdded = myGoals[term]?.some(g => g.id === goal.id);
                const selectedClass = isAdded ? 'selected' : '';
                const buttonText = isAdded ? 'Added' : 'Add';
                const buttonDisabled = isAdded ? 'disabled' : '';

                return `
                    <div class="available-goal ${selectedClass}" data-id="${goal.id}" data-term="${term}">
                        <div class="goal-name">${goal.name}</div>
                        <div class="goal-meta">
                            <span class="goal-category">${goal.category}</span>
                            <span class="goal-priority ${goal.priority}">${getPriorityLabel(goal.priority)}</span>
                        </div>
                        <button class="btn add-goal" ${buttonDisabled} style="margin-top: 10px;">${buttonText}</button>
                    </div>
                `;
            }

            // Add event handlers for goals
            function addGoalEventListeners() {
                // Handlers for checkboxes
                document.querySelectorAll('.goal-checkbox').forEach(checkbox => {
                    checkbox.addEventListener('change', async (e) => {
                        const goalItem = e.target.closest('.goal-item');
                        const goalId = parseInt(goalItem.getAttribute('data-id'));
                        const term = goalItem.getAttribute('data-term');
                        const completed = e.target.checked;

                        try {
                            const response = await fetch('/api/toggle_goal', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    goal_id: goalId,
                                    term: term,
                                    completed: completed
                                })
                            });

                            if (response.ok) {
                                const result = await response.json();
                                if (result.success) {
                                    userData = result.user_data;
                                    updateGoals();
                                }
                            }
                        } catch (error) {
                            console.error('Error updating goal:', error);
                        }
                    });
                });

                // Handlers for delete buttons
                document.querySelectorAll('.remove-goal').forEach(button => {
                    button.addEventListener('click', async (e) => {
                        const goalItem = e.target.closest('.goal-item');
                        const goalId = parseInt(goalItem.getAttribute('data-id'));
                        const term = goalItem.getAttribute('data-term');

                        try {
                            const response = await fetch('/api/remove_goal', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    goal_id: goalId,
                                    term: term
                                })
                            });

                            if (response.ok) {
                                const result = await response.json();
                                if (result.success) {
                                    userData = result.user_data;
                                    updateGoals();
                                }
                            }
                        } catch (error) {
                            console.error('Error removing goal:', error);
                        }
                    });
                });
            }

            // Add event handlers for available goals
            function addAvailableGoalEventListeners() {
                document.querySelectorAll('.add-goal').forEach(button => {
                    button.addEventListener('click', async (e) => {
                        const goalItem = e.target.closest('.available-goal');
                        const goalId = parseInt(goalItem.getAttribute('data-id'));
                        const term = goalItem.getAttribute('data-term');

                        try {
                            const response = await fetch('/api/add_goal', {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    goal_id: goalId,
                                    term: term
                                })
                            });

                            if (response.ok) {
                                const result = await response.json();
                                if (result.success) {
                                    userData = result.user_data;
                                    updateGoals();
                                }
                            }
                        } catch (error) {
                            console.error('Error adding goal:', error);
                        }
                    });
                });
            }

            // Toggle goal tabs
            document.querySelectorAll('.goal-tab').forEach(tab => {
                tab.addEventListener('click', () => {
                    // Remove active class from all tabs
                    document.querySelectorAll('.goal-tab').forEach(t => {
                        t.classList.remove('active');
                    });

                    // Add active class to current tab
                    tab.classList.add('active');

                    // Hide all goal lists
                    document.querySelectorAll('.goals-list').forEach(list => {
                        list.classList.remove('active');
                    });

                    // Show selected goal list
                    const tabId = tab.getAttribute('data-tab');
                    document.getElementById(`${tabId}-list`).classList.add('active');
                });
            });

            // Load and display career paths
            async function updateCareerPaths() {
                try {
                    const response = await fetch('/api/career_paths');
                    const careerPaths = await response.json();

                    let html = '';
                    for (const [path, data] of Object.entries(careerPaths)) {
                        const isSelected = userData.career_path === path;
                        html += `
                            <div class="career-path ${isSelected ? 'selected' : ''}" data-path="${path}">
                                <div class="career-title">${path}</div>
                                <div class="career-description">${data.description}</div>
                                <div class="skills-list">
                                    ${data.skills.map(skill => `<div class="skill-tag">${skill}</div>`).join('')}
                                </div>
                            </div>
                        `;
                    }

                    document.getElementById('career-paths-list').innerHTML = html;

                    // Career path selection handlers
                    document.querySelectorAll('.career-path').forEach(element => {
                        element.addEventListener('click', async () => {
                            const path = element.getAttribute('data-path');

                            try {
                                const response = await fetch('/api/select_career', {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json'
                                    },
                                    body: JSON.stringify({ career_path: path })
                                });

                                if (response.ok) {
                                    await loadUserData();
                                }
                            } catch (error) {
                                console.error('Error selecting career path:', error);
                            }
                        });
                    });
                } catch (error) {
                    console.error('Error loading career paths:', error);
                }
            }

            // Load and display quests
            async function updateQuests() {
                try {
                    const response = await fetch('/api/quests');
                    const quests = await response.json();

                    let html = '';
                    quests.forEach(quest => {
                        const isCompleted = userData.completed_quests.includes(quest.id);

                        html += `
                            <div class="quest-item">
                                <div class="quest-info">
                                    <div class="quest-name">${quest.name}</div>
                                    <div class="quest-meta">
                                        <span><i class="fas fa-star"></i> ${quest.xp} XP</span>
                                        <span><i class="fas fa-coins"></i> ${quest.coins} coins</span>
                                        <span><i class="fas fa-tag"></i> ${quest.skill}</span>
                                    </div>
                                    <div class="quest-type">${getQuestTypeLabel(quest.type)}</div>
                                </div>
                                <button class="btn complete-quest" data-id="${quest.id}" ${isCompleted ? 'disabled' : ''}>
                                    ${isCompleted ? 'Completed' : 'Complete'}
                                </button>
                            </div>
                        `;
                    });

                    document.getElementById('quests-list').innerHTML = html;

                    // Quest completion handlers
                    document.querySelectorAll('.complete-quest').forEach(button => {
                        button.addEventListener('click', async () => {
                            const questId = parseInt(button.getAttribute('data-id'));

                            try {
                                const response = await fetch(`/api/complete_quest/${questId}`, {
                                    method: 'POST'
                                });

                                if (response.ok) {
                                    const result = await response.json();
                                    if (result.success) {
                                        userData = result.user_data;
                                        updateUI();

                                        // Show notification
                                        alert('Quest completed! Rewards received.');
                                    }
                                }
                            } catch (error) {
                                console.error('Error completing quest:', error);
                            }
                        });
                    });
                } catch (error) {
                    console.error('Error loading quests:', error);
                }
            }

            // Get quest type label
            function getQuestTypeLabel(type) {
                const labels = {
                    'education': 'Education',
                    'reading': 'Reading',
                    'social': 'Social',
                    'practice': 'Practice'
                };
                return labels[type] || type;
            }

            // Update badges
            function updateBadges() {
                let html = '';
                for (const [badgeId, badge] of Object.entries(BADGES)) {
                    const hasBadge = userData.badges.includes(badgeId);

                    html += `
                        <div class="badge ${hasBadge ? '' : 'locked'}">
                            <div class="badge-icon">${badge.icon}</div>
                            <div class="badge-name">${badge.name}</div>
                            <div class="badge-description">${badge.description}</div>
                            <div style="margin-top: 10px; font-size: 12px;">
                                ${hasBadge ? '<span style="color: green;">Earned</span>' : '<span style="color: #999;">Not earned</span>'}
                            </div>
                        </div>
                    `;
                }

                document.getElementById('badges-container').innerHTML = html;
            }

            // Navigation between sections
            document.querySelectorAll('.nav-item').forEach(item => {
                item.addEventListener('click', () => {
                    // Remove active class from all items
                    document.querySelectorAll('.nav-item').forEach(i => {
                        i.classList.remove('active');
                    });

                    // Add active class to current item
                    item.classList.add('active');

                    // Hide all sections
                    document.querySelectorAll('.content-section').forEach(section => {
                        section.classList.remove('active');
                    });

                    // Show selected section
                    const sectionId = item.getAttribute('data-section');
                    document.getElementById(sectionId).classList.add('active');

                    // Update page title
                    const titles = {
                        'dashboard': 'Dashboard',
                        'career': 'Career Map',
                        'quests': 'Quests',
                        'ai': 'AI Assistant',
                        'achievements': 'Achievements',
                        'profile': 'Personal Account'
                    };

                    document.getElementById('page-title').textContent = titles[sectionId] || 'Internal Growth';
                });
            });

            // AI Chat
            document.getElementById('send-message').addEventListener('click', sendMessage);
            document.getElementById('chat-input').addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });

            async function sendMessage() {
                const input = document.getElementById('chat-input');
                const message = input.value.trim();

                if (!message) return;

                // Add user message to chat
                addMessageToChat(message, 'user');
                input.value = '';

                try {
                    // Send message to AI
                    const response = await fetch('/api/ai_chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ message })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        // Add AI response to chat
                        addMessageToChat(data.response, 'ai');
                    }
                } catch (error) {
                    console.error('Error sending message:', error);
                    addMessageToChat('Sorry, an error occurred. Please try again later.', 'ai');
                }
            }

            function addMessageToChat(message, sender) {
                const chatMessages = document.getElementById('chat-messages');
                const messageElement = document.createElement('div');
                messageElement.className = `message ${sender}-message`;
                messageElement.textContent = message;

                chatMessages.appendChild(messageElement);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }

            // Initialize on page load
            document.addEventListener('DOMContentLoaded', () => {
                loadUserData();
            });
        </script>
    </body>
    </html>
    '''


# API endpoints
@app.route('/api/user')
def get_user():
    return jsonify(get_user_data())


@app.route('/api/career_paths')
def get_career_paths():
    return jsonify(CAREER_PATHS)


@app.route('/api/quests')
def get_quests():
    return jsonify(QUESTS)


@app.route('/api/career_goals')
def get_career_goals():
    return jsonify(CAREER_GOALS)


@app.route('/api/complete_quest/<int:quest_id>', methods=['POST'])
def complete_quest(quest_id):
    user_data = get_user_data()
    quest = next((q for q in QUESTS if q['id'] == quest_id), None)

    if quest and quest_id not in user_data['completed_quests']:
        # Update main metrics
        user_data['xp'] += quest['xp']
        user_data['coins'] += quest['coins']
        user_data['completed_quests'].append(quest_id)

        # Update statistics
        user_data['total_quests_completed'] = len(user_data['completed_quests'])
        user_data['total_xp_earned'] = user_data.get('total_xp_earned', 0) + quest['xp']
        user_data['total_coins_earned'] = user_data.get('total_coins_earned', 0) + quest['coins']

        # Update quest type statistics
        quest_type = quest['type']
        if quest_type in user_data['quests_by_type']:
            user_data['quests_by_type'][quest_type] += 1
        else:
            user_data['quests_by_type'][quest_type] = 1

        # Update skills progress
        update_skills_progress(user_data, quest['skill'], quest['xp'])

        # Update last activity
        user_data['last_activity'] = datetime.now().strftime("%m/%d/%Y %H:%M")

        # Increase streak (simplified logic)
        user_data['learning_streak'] = user_data.get('learning_streak', 1) + 1

        # Check level up
        xp_needed = user_data['level'] * 100
        if user_data['xp'] >= xp_needed:
            user_data['level'] += 1
            user_data['xp'] = 0

        # Check badges
        if quest['skill'] == 'Python' and 'python_beginner' not in user_data['badges']:
            user_data['badges'].append('python_beginner')

        if len(user_data['completed_quests']) >= 3 and 'active_learner' not in user_data['badges']:
            user_data['badges'].append('active_learner')

        if len(user_data['completed_quests']) >= 5 and 'quest_master' not in user_data['badges']:
            user_data['badges'].append('quest_master')

        session.modified = True
        return jsonify({'success': True, 'user_data': user_data})

    return jsonify({'success': False})


@app.route('/api/ai_chat', methods=['POST'])
def ai_chat():
    data = request.get_json()
    user_message = data.get('message', '')
    response = ai_assistant_response(user_message)
    return jsonify({'response': response})


@app.route('/api/select_career', methods=['POST'])
def select_career():
    data = request.get_json()
    career_path = data.get('career_path')
    user_data = get_user_data()
    user_data['career_path'] = career_path
    session.modified = True
    return jsonify({'success': True})


@app.route('/api/add_goal', methods=['POST'])
def add_goal():
    data = request.get_json()
    goal_id = data.get('goal_id')
    term = data.get('term')

    user_data = get_user_data()

    # Initialize goals structure if it doesn't exist
    if 'career_goals' not in user_data:
        user_data['career_goals'] = {
            'short_term': [],
            'medium_term': [],
            'long_term': []
        }

    # Check if goal already exists
    existing_goal = next((g for g in user_data['career_goals'][term] if g['id'] == goal_id), None)

    if not existing_goal:
        # Find goal in predefined list
        goal_to_add = None
        for goal in CAREER_GOALS[term]:
            if goal['id'] == goal_id:
                goal_to_add = goal.copy()
                goal_to_add['completed'] = False
                break

        if goal_to_add:
            user_data['career_goals'][term].append(goal_to_add)
            session.modified = True
            return jsonify({'success': True, 'user_data': user_data})

    return jsonify({'success': False})


@app.route('/api/remove_goal', methods=['POST'])
def remove_goal():
    data = request.get_json()
    goal_id = data.get('goal_id')
    term = data.get('term')

    user_data = get_user_data()

    if 'career_goals' in user_data and term in user_data['career_goals']:
        user_data['career_goals'][term] = [g for g in user_data['career_goals'][term] if g['id'] != goal_id]
        session.modified = True
        return jsonify({'success': True, 'user_data': user_data})

    return jsonify({'success': False})


@app.route('/api/toggle_goal', methods=['POST'])
def toggle_goal():
    data = request.get_json()
    goal_id = data.get('goal_id')
    term = data.get('term')
    completed = data.get('completed', False)

    user_data = get_user_data()

    if 'career_goals' in user_data and term in user_data['career_goals']:
        for goal in user_data['career_goals'][term]:
            if goal['id'] == goal_id:
                goal['completed'] = completed
                session.modified = True
                return jsonify({'success': True, 'user_data': user_data})

    return jsonify({'success': False})


if __name__ == '__main__':
    app.run(debug=True, port=5000)
