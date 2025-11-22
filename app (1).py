from flask import Flask, request, jsonify, session
import json
import random
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'career_autopilot_secret_key'

# Моковые данные для демонстрации
CAREER_PATHS = {
    "Data Scientist": {
        "skills": ["Python", "SQL", "Машинное обучение", "Статистика", "Data Visualization"],
        "description": "Специалист по анализу данных и построению ML-моделей"
    },
    "Frontend Developer": {
        "skills": ["JavaScript", "React", "HTML/CSS", "TypeScript", "UI/UX"],
        "description": "Разработчик пользовательских интерфейсов"
    },
    "Project Manager": {
        "skills": ["Управление проектами", "Коммуникация", "Agile", "Презентации", "Лидерство"],
        "description": "Руководитель проектов и команд"
    }
}

QUESTS = [
    {"id": 1, "name": "Пройди курс по Python", "xp": 100, "coins": 50, "skill": "Python", "type": "education"},
    {"id": 2, "name": "Посмотри вебинар по Agile", "xp": 80, "coins": 40, "skill": "Agile", "type": "education"},
    {"id": 3, "name": "Прочитай статью о React", "xp": 60, "coins": 30, "skill": "React", "type": "reading"},
    {"id": 4, "name": "Попроси фидбэк у коллеги", "xp": 120, "coins": 60, "skill": "Коммуникация", "type": "social"},
    {"id": 5, "name": "Реши задачу по алгоритмам", "xp": 150, "coins": 75, "skill": "Python", "type": "practice"},
    {"id": 6, "name": "Подготовь презентацию", "xp": 90, "coins": 45, "skill": "Презентации", "type": "practice"}
]

BADGES = {
    "python_beginner": {"name": "Новичок Python", "description": "Выполнил первое задание по Python", "icon": "🐍"},
    "active_learner": {"name": "Активный ученик", "description": "Выполнил 5 заданий", "icon": "⭐"},
    "team_player": {"name": "Командный игрок", "description": "Получил фидбэк от коллеги", "icon": "👥"},
    "ml_master": {"name": "Мастер ML", "description": "Освоил машинное обучение", "icon": "🤖"},
    "quest_master": {"name": "Мастер квестов", "description": "Выполнил 10 заданий", "icon": "🏆"},
    "skill_collector": {"name": "Коллекционер навыков", "description": "Изучил 5 различных навыков", "icon": "📚"}
}

# Предопределенные цели для выбора
CAREER_GOALS = {
    "short_term": [
        {"id": 1, "name": "Освоить базовый синтаксис Python", "category": "Программирование", "priority": "high"},
        {"id": 2, "name": "Изучить основы SQL", "category": "Базы данных", "priority": "medium"},
        {"id": 3, "name": "Понять основные принципы ООП", "category": "Программирование", "priority": "high"},
        {"id": 4, "name": "Научиться работать с Git", "category": "Инструменты", "priority": "medium"},
        {"id": 5, "name": "Освоить основы алгоритмов", "category": "Программирование", "priority": "medium"}
    ],
    "medium_term": [
        {"id": 6, "name": "Разработать собственный проект", "category": "Практика", "priority": "high"},
        {"id": 7, "name": "Изучить фреймворк Django/Flask", "category": "Программирование", "priority": "medium"},
        {"id": 8, "name": "Освоить основы машинного обучения", "category": "Data Science", "priority": "medium"},
        {"id": 9, "name": "Научиться работать с Docker", "category": "Инфраструктура", "priority": "low"},
        {"id": 10, "name": "Изучить основы веб-разработки", "category": "Web", "priority": "medium"}
    ],
    "long_term": [
        {"id": 11, "name": "Стать Middle-разработчиком", "category": "Карьера", "priority": "high"},
        {"id": 12, "name": "Участвовать в опенсорс проекте", "category": "Практика", "priority": "medium"},
        {"id": 13, "name": "Подготовиться к техническому собеседованию", "category": "Карьера", "priority": "high"},
        {"id": 14, "name": "Освоить продвинутые алгоритмы", "category": "Программирование", "priority": "medium"},
        {"id": 15, "name": "Изучить архитектуру приложений", "category": "Архитектура", "priority": "medium"}
    ]
}

# Предопределенные ответы ИИ-помощника
AI_RESPONSES = {
    "привет": "Привет! Я ваш ИИ-помощник по карьере. Чем могу помочь в вашем профессиональном развитии?",
    "как дела": "Всё отлично! Готов помочь вам с карьерными вопросами и развитием навыков.",
    "что ты умеешь": "Я могу помочь с выбором карьерного пути, подобрать задания для развития навыков, отслеживать прогресс и ставить цели.",
    "карьера": "Проанализировав ваш профиль, я вижу потенциал в области Data Science. Рекомендую начать с основ Python и статистики.",
    "навыки": "Ваши текущие навыки: Python (65%), SQL (40%). Для выбранного пути рекомендую изучить машинное обучение и визуализацию данных.",
    "план": "Ваш карьерный план:\n1. Освоить Python (2 недели)\n2. Изучить SQL (3 недели)\n3. Основы ML (4 недели)\n4. Реальные проекты (2 месяца)",
    "квесты": "Сегодня доступны квесты по Python, Agile и командной работе. Выберите то, что больше соответствует вашим целям!",
    "статистика": "Проверьте раздел 'Личный кабинет' для просмотра вашей подробной статистики и прогресса по навыкам.",
    "цели": "В личном кабинете вы можете выбрать и отслеживать свои карьерные цели. Я помогу подобрать подходящие цели для вашего развития.",
    "default": "Я здесь, чтобы помочь с вашим карьерным развитием. Спросите о навыках, карьерном плане, доступных заданиях или рекомендациях."
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
                "Машинное обучение": 20,
                "Статистика": 30,
                "Data Visualization": 25,
                "JavaScript": 10,
                "React": 5,
                "HTML/CSS": 15,
                "TypeScript": 0,
                "UI/UX": 10,
                "Управление проектами": 35,
                "Коммуникация": 60,
                "Agile": 45,
                "Презентации": 50,
                "Лидерство": 40
            },
            'join_date': datetime.now().strftime("%d.%m.%Y"),
            'total_quests_completed': 0,
            'total_xp_earned': 0,
            'total_coins_earned': 0,
            'quests_by_type': {
                'education': 0,
                'reading': 0,
                'social': 0,
                'practice': 0
            },
            'last_activity': datetime.now().strftime("%d.%m.%Y %H:%M"),
            'learning_streak': 1,
            'career_goals': {
                'short_term': [],
                'medium_term': [],
                'long_term': []
            }
        }
    return session['user_data']


def update_skills_progress(user_data, skill, xp_earned):
    """Обновление прогресса навыков на основе полученного опыта"""
    if skill in user_data['skills_progress']:
        progress_increase = min(xp_earned / 10, 10)
        user_data['skills_progress'][skill] = min(
            user_data['skills_progress'][skill] + progress_increase,
            100
        )
    else:
        user_data['skills_progress'][skill] = min(xp_earned / 5, 20)


def ai_assistant_response(message):
    """Упрощенный ИИ-помощник с предопределенными ответами"""
    message_lower = message.lower()

    # Поиск ключевых слов в сообщении
    for key, response in AI_RESPONSES.items():
        if key in message_lower and key != "default":
            return response

    # Если ключевые слова не найдены, возвращаем ответ по умолчанию
    return AI_RESPONSES["default"]


@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Внутренний рост | Холдинг Т1</title>
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

            /* Сайдбар */
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

            /* Основной контент */
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

            /* Карточки */
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

            /* Квесты */
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

            /* Чат с ИИ */
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

            /* Карьерные пути */
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

            /* Бейджи */
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

            /* Личный кабинет */
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

            /* Цели */
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

            /* Адаптивность */
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
            <!-- Сайдбар -->
            <div class="sidebar">
                <div class="logo">
                    <i class="fas fa-rocket"></i>
                    <h1>Внутренний рост</h1>
                </div>

                <div class="user-profile">
                    <div class="avatar">
                        <i class="fas fa-user"></i>
                    </div>
                    <div class="user-level">Уровень <span id="user-level">1</span></div>
                    <div class="progress-container">
                        <div class="progress-bar">
                            <div class="progress-fill" id="xp-progress" style="width: 0%"></div>
                        </div>
                    </div>
                    <div class="stats">
                        <div class="stat-item">
                            <div class="stat-value" id="user-xp">0</div>
                            <div class="stat-label">Опыт</div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-value" id="user-coins">0</div>
                            <div class="stat-label">Монеты</div>
                        </div>
                    </div>
                </div>

                <div class="nav-menu">
                    <div class="nav-item active" data-section="dashboard">
                        <i class="fas fa-home"></i>
                        <span>Главная</span>
                    </div>
                    <div class="nav-item" data-section="career">
                        <i class="fas fa-map"></i>
                        <span>Карьерная карта</span>
                    </div>
                    <div class="nav-item" data-section="quests">
                        <i class="fas fa-tasks"></i>
                        <span>Квесты</span>
                    </div>
                    <div class="nav-item" data-section="ai">
                        <i class="fas fa-robot"></i>
                        <span>ИИ-помощник</span>
                    </div>
                    <div class="nav-item" data-section="achievements">
                        <i class="fas fa-trophy"></i>
                        <span>Достижения</span>
                    </div>
                    <div class="nav-item" data-section="profile">
                        <i class="fas fa-user-circle"></i>
                        <span>Личный кабинет</span>
                    </div>
                </div>

                <div class="footer">
                    <div class="company">Холдинг Т1</div>
                </div>
            </div>

            <!-- Основной контент -->
            <div class="main-content">
                <div class="header">
                    <h2 id="page-title">Главная панель</h2>
                    <div class="date-display" id="current-date"></div>
                </div>

                <!-- Главная -->
                <div class="content-section active" id="dashboard">
                    <div class="section-title">
                        <i class="fas fa-tachometer-alt"></i>
                        <span>Обзор прогресса</span>
                    </div>

                    <div class="cards-container">
                        <div class="card">
                            <div class="card-title">
                                <i class="fas fa-chart-line"></i>
                                <span>Ваш прогресс</span>
                            </div>
                            <div id="progress-stats">
                                Загрузка...
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-title">
                                <i class="fas fa-star"></i>
                                <span>Ближайшие цели</span>
                            </div>
                            <div id="next-goals">
                                Загрузка...
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-title">
                                <i class="fas fa-bullseye"></i>
                                <span>Активные квесты</span>
                            </div>
                            <div id="active-quests">
                                Загрузка...
                            </div>
                        </div>
                    </div>

                    <div class="section-title">
                        <i class="fas fa-road"></i>
                        <span>Ваш карьерный путь</span>
                    </div>

                    <div id="user-career-path">
                        <p>Вы еще не выбрали карьерный путь. Перейдите в раздел "Карьерная карта" для выбора.</p>
                    </div>
                </div>

                <!-- Карьерная карта -->
                <div class="content-section" id="career">
                    <div class="section-title">
                        <i class="fas fa-map"></i>
                        <span>Выберите карьерный путь</span>
                    </div>

                    <p style="margin-bottom: 20px;">Выберите направление, в котором хотите развиваться. ИИ-помощник создаст персональный план развития.</p>

                    <div id="career-paths-list">
                        Загрузка карьерных путей...
                    </div>
                </div>

                <!-- Квесты -->
                <div class="content-section" id="quests">
                    <div class="section-title">
                        <i class="fas fa-tasks"></i>
                        <span>Доступные квесты</span>
                    </div>

                    <p style="margin-bottom: 20px;">Выполняйте задания для получения опыта, монет и бейджей.</p>

                    <div id="quests-list">
                        Загрузка квестов...
                    </div>
                </div>

                <!-- ИИ-помощник -->
                <div class="content-section" id="ai">
                    <div class="section-title">
                        <i class="fas fa-robot"></i>
                        <span>ИИ-помощник по карьере</span>
                    </div>

                    <p style="margin-bottom: 20px;">Задайте вопрос о вашем карьерном развитии, навыках или доступных заданиях.</p>

                    <div class="chat-container">
                        <div class="chat-messages" id="chat-messages">
                            <div class="message ai-message">
                                Привет! Я ваш ИИ-помощник по карьерному развитию. Задайте мне вопрос о ваших навыках, карьерном плане или доступных заданиях.
                            </div>
                        </div>
                        <div class="chat-input">
                            <input type="text" id="chat-input" placeholder="Введите ваш вопрос...">
                            <button id="send-message">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                    </div>
                </div>

                <!-- Достижения -->
                <div class="content-section" id="achievements">
                    <div class="section-title">
                        <i class="fas fa-trophy"></i>
                        <span>Ваши достижения</span>
                    </div>

                    <div class="badges-container" id="badges-container">
                        Загрузка бейджей...
                    </div>
                </div>

                <!-- Личный кабинет -->
                <div class="content-section" id="profile">
                    <div class="section-title">
                        <i class="fas fa-user-circle"></i>
                        <span>Личный кабинет</span>
                    </div>

                    <div class="profile-header">
                        <div class="profile-avatar">
                            <i class="fas fa-user"></i>
                        </div>
                        <div class="profile-info">
                            <h3 id="profile-username">Сотрудник Холдинг Т1</h3>
                            <p id="profile-career-path">Карьерный путь: Не выбран</p>
                            <p id="profile-join-date">В команде с: Загрузка...</p>
                            <p id="profile-last-activity">Последняя активность: Загрузка...</p>
                        </div>
                    </div>

                    <div class="stats-grid">
                        <div class="stat-card">
                            <i class="fas fa-chart-line"></i>
                            <div class="stat-card-value" id="stat-level">1</div>
                            <div class="stat-card-label">Текущий уровень</div>
                        </div>
                        <div class="stat-card">
                            <i class="fas fa-star"></i>
                            <div class="stat-card-value" id="stat-total-xp">0</div>
                            <div class="stat-card-label">Всего опыта</div>
                        </div>
                        <div class="stat-card">
                            <i class="fas fa-coins"></i>
                            <div class="stat-card-value" id="stat-total-coins">0</div>
                            <div class="stat-card-label">Всего монет</div>
                        </div>
                        <div class="stat-card">
                            <i class="fas fa-tasks"></i>
                            <div class="stat-card-value" id="stat-total-quests">0</div>
                            <div class="stat-card-label">Выполнено квестов</div>
                        </div>
                        <div class="stat-card">
                            <i class="fas fa-trophy"></i>
                            <div class="stat-card-value" id="stat-badges">0</div>
                            <div class="stat-card-label">Получено бейджей</div>
                        </div>
                        <div class="stat-card">
                            <i class="fas fa-fire"></i>
                            <div class="stat-card-value" id="stat-streak">1</div>
                            <div class="stat-card-label">Дней подряд</div>
                        </div>
                    </div>

                    <div class="skills-progress">
                        <h3 style="margin-bottom: 20px; color: var(--dark-blue);">Прогресс по навыкам</h3>
                        <div id="skills-progress-list">
                            Загрузка навыков...
                        </div>
                    </div>

                    <div class="quests-stats">
                        <h3 style="margin-bottom: 20px; color: var(--dark-blue);">Статистика по квестам</h3>
                        <div class="quest-type-stats" id="quests-type-stats">
                            <!-- Будет заполнено через JavaScript -->
                        </div>
                    </div>

                    <!-- Новый раздел: Мои цели -->
                    <div class="goals-section">
                        <h3 style="margin-bottom: 20px; color: var(--dark-blue);">Мои карьерные цели</h3>

                        <div class="goals-tabs">
                            <div class="goal-tab active" data-tab="my-goals">Мои цели</div>
                            <div class="goal-tab" data-tab="available-goals">Доступные цели</div>
                        </div>

                        <div class="goals-list active" id="my-goals-list">
                            <div id="my-goals-content">
                                Загрузка ваших целей...
                            </div>
                        </div>

                        <div class="goals-list" id="available-goals-list">
                            <div class="available-goals" id="available-goals-content">
                                Загрузка доступных целей...
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Текущий пользователь
            let userData = {};

            // Загрузка данных пользователя
            async function loadUserData() {
                try {
                    const response = await fetch('/api/user');
                    userData = await response.json();
                    updateUI();
                } catch (error) {
                    console.error('Ошибка загрузки данных:', error);
                }
            }

            // Обновление интерфейса
            function updateUI() {
                // Обновление сайдбара
                document.getElementById('user-level').textContent = userData.level;
                document.getElementById('user-xp').textContent = userData.xp;
                document.getElementById('user-coins').textContent = userData.coins;

                // Прогресс бар
                const xpNeeded = userData.level * 100;
                const progressPercent = (userData.xp / xpNeeded) * 100;
                document.getElementById('xp-progress').style.width = `${progressPercent}%`;

                // Обновление даты
                const now = new Date();
                document.getElementById('current-date').textContent = now.toLocaleDateString('ru-RU', {
                    weekday: 'long',
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric'
                });

                // Обновление разделов
                updateDashboard();
                updateCareerPaths();
                updateQuests();
                updateBadges();
                updateProfile();
                updateGoals();
            }

            // Обновление главной панели
            function updateDashboard() {
                // Статистика прогресса
                document.getElementById('progress-stats').innerHTML = `
                    <p>Уровень: <strong>${userData.level}</strong></p>
                    <p>Опыт: <strong>${userData.xp}/${userData.level * 100}</strong></p>
                    <p>Монеты: <strong>${userData.coins}</strong></p>
                    <p>Выполнено квестов: <strong>${userData.completed_quests.length}</strong></p>
                `;

                // Ближайшие цели
                document.getElementById('next-goals').innerHTML = `
                    <p>• Достичь уровня ${userData.level + 1}</p>
                    <p>• Выполнить 3 квеста для бейджа "Активный ученик"</p>
                    <p>• Изучить Python для бейджа "Новичок Python"</p>
                `;

                // Активные квесты
                const activeQuestsCount = Math.min(3, 6 - userData.completed_quests.length);
                document.getElementById('active-quests').innerHTML = `
                    <p>У вас <strong>${activeQuestsCount}</strong> активных квестов</p>
                    <p>Перейдите в раздел "Квесты" для просмотра</p>
                `;

                // Карьерный путь
                if (userData.career_path) {
                    document.getElementById('user-career-path').innerHTML = `
                        <div class="career-path selected">
                            <div class="career-title">${userData.career_path}</div>
                            <p>Вы активно развиваетесь в этом направлении. Продолжайте выполнять квесты для продвижения по карьерной лестнице!</p>
                        </div>
                    `;
                }
            }

            // Обновление личного кабинета
            function updateProfile() {
                // Основная информация
                document.getElementById('profile-username').textContent = 'Сотрудник Холдинг Т1';
                document.getElementById('profile-career-path').textContent = 
                    userData.career_path ? `Карьерный путь: ${userData.career_path}` : 'Карьерный путь: Не выбран';
                document.getElementById('profile-join-date').textContent = `В команде с: ${userData.join_date}`;
                document.getElementById('profile-last-activity').textContent = `Последняя активность: ${userData.last_activity}`;

                // Статистика
                document.getElementById('stat-level').textContent = userData.level;
                document.getElementById('stat-total-xp').textContent = userData.total_xp_earned || userData.xp;
                document.getElementById('stat-total-coins').textContent = userData.total_coins_earned || userData.coins;
                document.getElementById('stat-total-quests').textContent = userData.total_quests_completed || userData.completed_quests.length;
                document.getElementById('stat-badges').textContent = userData.badges.length;
                document.getElementById('stat-streak').textContent = userData.learning_streak || 1;

                // Прогресс по навыкам
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

                // Статистика по типам квестов
                if (userData.quests_by_type) {
                    const questTypes = {
                        'education': { icon: 'fas fa-graduation-cap', label: 'Обучение' },
                        'reading': { icon: 'fas fa-book', label: 'Чтение' },
                        'social': { icon: 'fas fa-users', label: 'Социальные' },
                        'practice': { icon: 'fas fa-laptop-code', label: 'Практика' }
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

            // Обновление целей
            async function updateGoals() {
                try {
                    // Загрузка доступных целей
                    const response = await fetch('/api/career_goals');
                    const availableGoals = await response.json();

                    // Отображение моих целей
                    displayMyGoals();

                    // Отображение доступных целей
                    displayAvailableGoals(availableGoals);

                } catch (error) {
                    console.error('Ошибка загрузки целей:', error);
                }
            }

            // Отображение моих целей
            function displayMyGoals() {
                const myGoals = userData.career_goals || {
                    'short_term': [],
                    'medium_term': [],
                    'long_term': []
                };

                let html = '';

                // Краткосрочные цели
                if (myGoals.short_term && myGoals.short_term.length > 0) {
                    html += `<h4 style="margin: 15px 0 10px 0; color: var(--dark-blue);">Краткосрочные цели</h4>`;
                    myGoals.short_term.forEach(goal => {
                        html += createGoalItem(goal, 'short_term');
                    });
                }

                // Среднесрочные цели
                if (myGoals.medium_term && myGoals.medium_term.length > 0) {
                    html += `<h4 style="margin: 15px 0 10px 0; color: var(--dark-blue);">Среднесрочные цели</h4>`;
                    myGoals.medium_term.forEach(goal => {
                        html += createGoalItem(goal, 'medium_term');
                    });
                }

                // Долгосрочные цели
                if (myGoals.long_term && myGoals.long_term.length > 0) {
                    html += `<h4 style="margin: 15px 0 10px 0; color: var(--dark-blue);">Долгосрочные цели</h4>`;
                    myGoals.long_term.forEach(goal => {
                        html += createGoalItem(goal, 'long_term');
                    });
                }

                if (!html) {
                    html = '<p>У вас пока нет выбранных целей. Перейдите во вкладку "Доступные цели", чтобы добавить цели для отслеживания.</p>';
                }

                document.getElementById('my-goals-content').innerHTML = html;

                // Добавляем обработчики событий для чекбоксов и кнопок удаления
                addGoalEventListeners();
            }

            // Создание элемента цели
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
                            <button class="btn btn-danger remove-goal">Удалить</button>
                        </div>
                    </div>
                `;
            }

            // Получение текстового представления приоритета
            function getPriorityLabel(priority) {
                const labels = {
                    'high': 'Высокий',
                    'medium': 'Средний',
                    'low': 'Низкий'
                };
                return labels[priority] || priority;
            }

            // Отображение доступных целей
            function displayAvailableGoals(availableGoals) {
                let html = '';

                // Краткосрочные цели
                html += `<h4 style="margin: 15px 0 10px 0; color: var(--dark-blue);">Краткосрочные цели</h4>`;
                availableGoals.short_term.forEach(goal => {
                    html += createAvailableGoalItem(goal, 'short_term');
                });

                // Среднесрочные цели
                html += `<h4 style="margin: 15px 0 10px 0; color: var(--dark-blue);">Среднесрочные цели</h4>`;
                availableGoals.medium_term.forEach(goal => {
                    html += createAvailableGoalItem(goal, 'medium_term');
                });

                // Долгосрочные цели
                html += `<h4 style="margin: 15px 0 10px 0; color: var(--dark-blue);">Долгосрочные цели</h4>`;
                availableGoals.long_term.forEach(goal => {
                    html += createAvailableGoalItem(goal, 'long_term');
                });

                document.getElementById('available-goals-content').innerHTML = html;

                // Добавляем обработчики событий для выбора целей
                addAvailableGoalEventListeners();
            }

            // Создание элемента доступной цели
            function createAvailableGoalItem(goal, term) {
                // Проверяем, добавлена ли уже цель
                const myGoals = userData.career_goals || {
                    'short_term': [],
                    'medium_term': [],
                    'long_term': []
                };

                const isAdded = myGoals[term]?.some(g => g.id === goal.id);
                const selectedClass = isAdded ? 'selected' : '';
                const buttonText = isAdded ? 'Добавлено' : 'Добавить';
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

            // Добавление обработчиков событий для целей
            function addGoalEventListeners() {
                // Обработчики для чекбоксов
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
                            console.error('Ошибка обновления цели:', error);
                        }
                    });
                });

                // Обработчики для кнопок удаления
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
                            console.error('Ошибка удаления цели:', error);
                        }
                    });
                });
            }

            // Добавление обработчиков событий для доступных целей
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
                            console.error('Ошибка добавления цели:', error);
                        }
                    });
                });
            }

            // Переключение вкладок целей
            document.querySelectorAll('.goal-tab').forEach(tab => {
                tab.addEventListener('click', () => {
                    // Убрать активный класс у всех вкладок
                    document.querySelectorAll('.goal-tab').forEach(t => {
                        t.classList.remove('active');
                    });

                    // Добавить активный класс к текущей вкладке
                    tab.classList.add('active');

                    // Скрыть все списки целей
                    document.querySelectorAll('.goals-list').forEach(list => {
                        list.classList.remove('active');
                    });

                    // Показать выбранный список целей
                    const tabId = tab.getAttribute('data-tab');
                    document.getElementById(`${tabId}-list`).classList.add('active');
                });
            });

            // Загрузка и отображение карьерных путей
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

                    // Обработчики выбора карьерного пути
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
                                console.error('Ошибка выбора карьерного пути:', error);
                            }
                        });
                    });
                } catch (error) {
                    console.error('Ошибка загрузки карьерных путей:', error);
                }
            }

            // Загрузка и отображение квестов
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
                                        <span><i class="fas fa-coins"></i> ${quest.coins} монет</span>
                                        <span><i class="fas fa-tag"></i> ${quest.skill}</span>
                                    </div>
                                    <div class="quest-type">${getQuestTypeLabel(quest.type)}</div>
                                </div>
                                <button class="btn complete-quest" data-id="${quest.id}" ${isCompleted ? 'disabled' : ''}>
                                    ${isCompleted ? 'Выполнено' : 'Выполнить'}
                                </button>
                            </div>
                        `;
                    });

                    document.getElementById('quests-list').innerHTML = html;

                    // Обработчики выполнения квестов
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

                                        // Показать уведомление
                                        alert('Квест выполнен! Получены награды.');
                                    }
                                }
                            } catch (error) {
                                console.error('Ошибка выполнения квеста:', error);
                            }
                        });
                    });
                } catch (error) {
                    console.error('Ошибка загрузки квестов:', error);
                }
            }

            // Получение метки типа квеста
            function getQuestTypeLabel(type) {
                const labels = {
                    'education': 'Обучение',
                    'reading': 'Чтение',
                    'social': 'Социальное',
                    'practice': 'Практика'
                };
                return labels[type] || type;
            }

            // Обновление бейджей
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
                                ${hasBadge ? '<span style="color: green;">Получен</span>' : '<span style="color: #999;">Не получен</span>'}
                            </div>
                        </div>
                    `;
                }

                document.getElementById('badges-container').innerHTML = html;
            }

            // Навигация по разделам
            document.querySelectorAll('.nav-item').forEach(item => {
                item.addEventListener('click', () => {
                    // Убрать активный класс у всех элементов
                    document.querySelectorAll('.nav-item').forEach(i => {
                        i.classList.remove('active');
                    });

                    // Добавить активный класс к текущему элементу
                    item.classList.add('active');

                    // Скрыть все разделы
                    document.querySelectorAll('.content-section').forEach(section => {
                        section.classList.remove('active');
                    });

                    // Показать выбранный раздел
                    const sectionId = item.getAttribute('data-section');
                    document.getElementById(sectionId).classList.add('active');

                    // Обновить заголовок страницы
                    const titles = {
                        'dashboard': 'Главная панель',
                        'career': 'Карьерная карта',
                        'quests': 'Квесты',
                        'ai': 'ИИ-помощник',
                        'achievements': 'Достижения',
                        'profile': 'Личный кабинет'
                    };

                    document.getElementById('page-title').textContent = titles[sectionId] || 'Внутренний рост';
                });
            });

            // Чат с ИИ
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

                // Добавить сообщение пользователя в чат
                addMessageToChat(message, 'user');
                input.value = '';

                try {
                    // Отправить сообщение ИИ
                    const response = await fetch('/api/ai_chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({ message })
                    });

                    if (response.ok) {
                        const data = await response.json();
                        // Добавить ответ ИИ в чат
                        addMessageToChat(data.response, 'ai');
                    }
                } catch (error) {
                    console.error('Ошибка отправки сообщения:', error);
                    addMessageToChat('Извините, произошла ошибка. Попробуйте позже.', 'ai');
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

            // Инициализация при загрузке страницы
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
        # Обновляем основные показатели
        user_data['xp'] += quest['xp']
        user_data['coins'] += quest['coins']
        user_data['completed_quests'].append(quest_id)

        # Обновляем статистику
        user_data['total_quests_completed'] = len(user_data['completed_quests'])
        user_data['total_xp_earned'] = user_data.get('total_xp_earned', 0) + quest['xp']
        user_data['total_coins_earned'] = user_data.get('total_coins_earned', 0) + quest['coins']

        # Обновляем статистику по типам квестов
        quest_type = quest['type']
        if quest_type in user_data['quests_by_type']:
            user_data['quests_by_type'][quest_type] += 1
        else:
            user_data['quests_by_type'][quest_type] = 1

        # Обновляем прогресс навыков
        update_skills_progress(user_data, quest['skill'], quest['xp'])

        # Обновляем последнюю активность
        user_data['last_activity'] = datetime.now().strftime("%d.%m.%Y %H:%M")

        # Увеличиваем streak (упрощенная логика)
        user_data['learning_streak'] = user_data.get('learning_streak', 1) + 1

        # Проверка повышения уровня
        xp_needed = user_data['level'] * 100
        if user_data['xp'] >= xp_needed:
            user_data['level'] += 1
            user_data['xp'] = 0

        # Проверка бейджей
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

    # Инициализируем структуру целей, если ее нет
    if 'career_goals' not in user_data:
        user_data['career_goals'] = {
            'short_term': [],
            'medium_term': [],
            'long_term': []
        }

    # Проверяем, есть ли уже такая цель
    existing_goal = next((g for g in user_data['career_goals'][term] if g['id'] == goal_id), None)

    if not existing_goal:
        # Находим цель в предопределенном списке
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
