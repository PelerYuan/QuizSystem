# 📚 Quiz System

A powerful, enterprise-ready web-based quiz system built with Flask that provides a comprehensive solution for creating, managing, and analyzing quizzes with advanced features and professional-grade performance.

![Quiz System](https://img.shields.io/badge/Flask-3.1.1-blue?logo=flask)
![Python](https://img.shields.io/badge/Python-3.11+-green?logo=python)
![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)
![License](https://img.shields.io/badge/License-GPL%20v3.0-red)

## ✨ Overview

The Quiz System is a feature-rich, scalable web application designed for educational institutions, businesses, and organizations that need to conduct online assessments. Built with modern web technologies and optimized for performance, it offers both a user-friendly interface for quiz takers and powerful administrative tools for quiz creators and managers.

### 🎯 Key Highlights

- **Visual Quiz Editor** - Drag-and-drop interface for creating quizzes
- **Advanced Analytics** - Comprehensive performance analysis with charts
- **Enterprise Deployment** - Production-ready Docker containerization
- **Multiple Question Types** - Single choice, multiple choice, and text input
- **Real-time Search & Sort** - Enhanced result management
- **Professional UI/UX** - Modern, responsive design

## 🚀 Features

### 👥 **User Experience**
- **Intuitive Quiz Interface** - Clean, responsive design for optimal quiz-taking experience
- **Multi-format Questions** - Support for text, images, and rich formatting
- **Immediate Feedback** - Real-time scoring and answer validation
- **Result Review** - Comprehensive review of completed quizzes with correct answers
- **Progress Tracking** - Visual progress indicators during quiz completion

### 🔧 **Administrative Tools**

#### **Visual Quiz Editor**
- **Drag-and-Drop Interface** - Intuitive question reordering and management
- **Real-time Preview** - See exactly how quizzes will appear to users
- **Image Upload Support** - Direct image integration for questions
- **Validation System** - Comprehensive error checking and guidance
- **Import/Export** - JSON-based quiz data management

#### **Advanced Analytics Dashboard**
- **Performance Metrics** - Average scores, pass rates, and statistical analysis
- **Visual Charts** - Score distribution and performance overview charts
- **Student Categorization** - Automatic identification of top performers and students needing attention
- **Export Capabilities** - Excel export for detailed analysis

#### **Enhanced Result Management**
- **Smart Search** - Real-time search by student name with cancel functionality
- **Advanced Sorting** - Sort by name, score, or date with visual indicators
- **Detailed Filtering** - Comprehensive result filtering and management
- **Bulk Operations** - Efficient management of large result sets

### 🛡️ **Security & Performance**
- **Role-based Access** - Secure admin authentication system
- **Input Validation** - Comprehensive data validation and sanitization
- **Session Management** - Secure session handling with timeout controls
- **Rate Limiting** - Built-in protection against abuse (Docker deployment)
- **Health Monitoring** - System health checks and performance monitoring

## 📦 Quick Start

### 🐳 **Docker Deployment (Recommended)**

For production or easy setup, use our optimized Docker deployment:

```bash
# 1. Clone the repository
git clone https://github.com/PelerYuan/QuizSystem
cd QuizSystem

# 2. Set up environment
cp .env.example .env
# Edit .env with your configuration

# 3. Deploy with one command
chmod +x deploy.sh
./deploy.sh prod --build
```

🔗 **[📖 Complete Docker Deployment Guide](DOCKER_DEPLOYMENT.md)**

The Docker deployment includes:
- **High-performance Nginx reverse proxy**
- **Gunicorn WSGI server** with auto-scaling
- **Redis caching** for improved performance
- **Health monitoring** and automatic recovery
- **SSL/TLS ready** configuration
- **Horizontal scaling** capabilities

### 💻 **Manual Installation**

For development or custom setups:

1. **Clone and Setup**:
   ```bash
   git clone https://github.com/PelerYuan/QuizSystem
   cd QuizSystem

   # Create necessary directories
   mkdir img quiz result tmp
   ```

2. **Virtual Environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database**:
   ```bash
   python -c "from app import db; db.create_all()"
   ```

5. **Run Application**:
   ```bash
   python app.py
   ```

6. **Access**: Navigate to `http://127.0.0.1:5000`

## 🎮 Usage Guide

### 🔐 **Admin Access**

1. **Login**: Navigate to `/admin_login` (password: `123456` by default)
2. **Dashboard**: Access comprehensive quiz management tools
3. **Create Quizzes**: Use the visual editor or import JSON files
4. **Manage Results**: View analytics and export data

### 📝 **Creating Quizzes**

#### **Visual Editor** (Recommended)
1. Click "Create New Quiz" from admin dashboard
2. Fill in quiz metadata (title, subtitle, description, points)
3. Add questions using the drag-and-drop interface
4. Upload images directly for questions
5. Preview and save your quiz

#### **JSON Import**
Upload JSON files with this structure:

```json
{
    "title": "Advanced Mathematics Quiz",
    "subtitle": "Calculus and Linear Algebra",
    "description": "Test your understanding of advanced mathematical concepts",
    "points": "5",
    "image_folder": "img",
    "questions": [
        {
            "Q": "What is the derivative of x²?",
            "options": [
                {"opt": "x"},
                {"opt": "2x", "correct": "true"},
                {"opt": "x²"},
                {"opt": "2x²"}
            ]
        },
        {
            "Q": "Select all prime numbers:",
            "multioptions": [
                {"opt": "2", "correct": "true"},
                {"opt": "3", "correct": "true"},
                {"opt": "4"},
                {"opt": "5", "correct": "true"}
            ]
        },
        {
            "Q": "Explain the concept of limits:",
            "input": "text"
        }
    ]
}
```

### 👨‍🎓 **Taking Quizzes**

1. **Access**: Use entrance URLs provided by administrators
2. **Registration**: Enter your name to begin
3. **Quiz Taking**: Navigate through questions with progress indicator
4. **Submission**: Review answers before final submission
5. **Results**: Immediate feedback with detailed review

## 🏗️ Project Architecture

```
QuizSystem/
├── 📱 Application Core
│   ├── app.py                     # Main Flask application
│   ├── configure.json             # Admin configuration
│   └── requirements*.txt          # Dependencies
│
├── 🗄️ Data Management
│   ├── data.sqlite                # Main database
│   ├── img/                       # Image storage
│   ├── quiz/                      # Quiz JSON files
│   ├── result/                    # Result storage
│   └── tmp/                       # Temporary files
│
├── 🎨 Frontend
│   ├── static/                    # CSS, JS, assets
│   │   ├── bootstrap.min.css      # UI framework
│   │   ├── codemirror.min.js      # Code editor
│   │   └── popper.min.js          # UI components
│   └── templates/                 # HTML templates
│       ├── admin/                 # Admin interface
│       │   ├── admin.html         # Main dashboard
│       │   ├── visual_editor.html # Quiz creator
│       │   ├── result_analytics.html # Analytics
│       │   └── manage_*.html      # Management pages
│       ├── index.html             # Home page
│       ├── quiz.html              # Quiz interface
│       └── review.html            # Results review
│
└── 🐳 Deployment
    ├── Dockerfile                 # Container definition
    ├── docker-compose.yml         # Service orchestration
    ├── nginx.conf                 # Reverse proxy config
    ├── gunicorn.conf.py          # WSGI server config
    ├── deploy.sh                  # Deployment automation
    └── maintenance.sh             # System maintenance
```

## 🛠️ Technology Stack

### **Backend Technologies**
- **Flask 3.1.1** - Modern Python web framework
- **SQLAlchemy** - Advanced ORM with database abstraction
- **Gunicorn** - Production-grade WSGI server
- **SQLite/PostgreSQL** - Flexible database options

### **Frontend Technologies**
- **Bootstrap 5** - Responsive UI framework
- **Chart.js** - Interactive data visualization
- **Font Awesome** - Professional icon library
- **CodeMirror** - Advanced text editor
- **SortableJS** - Drag-and-drop functionality

### **DevOps & Deployment**
- **Docker & Docker Compose** - Containerization
- **Nginx** - High-performance reverse proxy
- **Redis** - Caching and session management
- **Prometheus & Grafana** - Monitoring (optional)

### **Development Tools**
- **Python 3.11+** - Modern Python features
- **openpyxl** - Excel export functionality
- **Werkzeug** - WSGI utilities and security

## 🔧 Configuration

### **Environment Variables**

Create a `.env` file for production deployment:

```bash
# Application Settings
FLASK_ENV=production
ADMIN_PASSWORD=your_secure_password

# Database (PostgreSQL upgrade)
POSTGRES_PASSWORD=your_postgres_password

# Security
SECRET_KEY=your_32_character_secret_key

# Performance
GUNICORN_WORKERS=4
```

### **Admin Configuration**

Modify `configure.json` for admin settings:

```json
{
  "admin password": "your-secure-admin-password"
}
```

## 📊 Performance & Scalability

### **Performance Features**
- **Optimized Database Queries** - Efficient data retrieval
- **Static File Caching** - Browser and proxy caching
- **Compression** - Gzip compression for all responses
- **Connection Pooling** - Database connection optimization
- **Multi-worker Architecture** - Concurrent request handling

### **Scalability Options**
- **Horizontal Scaling** - Multiple application instances
- **Load Balancing** - Nginx upstream configuration
- **Database Scaling** - PostgreSQL cluster support
- **Caching Layers** - Redis and browser caching
- **CDN Ready** - Static asset optimization

## 🚀 Deployment Options

### **Development**
```bash
python app.py
# Access: http://localhost:5000
```

### **Production (Docker)**
```bash
./deploy.sh prod --build
# Access: http://localhost
# Includes: Nginx, Gunicorn, Redis, Health checks
```

### **Enterprise (Kubernetes)**
```bash
# Coming soon - Kubernetes manifests
# Features: Auto-scaling, Service mesh, Monitoring
```

## 🛡️ Security Features

- **Authentication** - Secure admin login system
- **Authorization** - Role-based access control
- **Input Validation** - Comprehensive data sanitization
- **CSRF Protection** - Built-in Flask security
- **Rate Limiting** - API abuse prevention
- **Security Headers** - XSS, clickjacking protection
- **SSL/TLS Ready** - HTTPS configuration included

## 📈 Monitoring & Analytics

### **Built-in Analytics**
- Performance metrics and score distributions
- Student categorization and progress tracking
- Export capabilities for detailed analysis
- Real-time health monitoring

### **Optional Monitoring Stack**
- **Prometheus** - Metrics collection
- **Grafana** - Data visualization
- **Health Checks** - Service monitoring
- **Log Aggregation** - Centralized logging

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

### **Development Setup**
```bash
# Clone your fork
git clone https://github.com/yourusername/QuizSystem
cd QuizSystem

# Set up development environment
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Run tests (coming soon)
python -m pytest

# Start development server
python app.py
```

## 📋 Roadmap

- [ ] **User Authentication System** - Multi-user support with roles
- [ ] **Quiz Templates** - Predefined quiz templates and themes
- [ ] **Advanced Question Types** - Fill-in-the-blank, matching, drag-and-drop
- [ ] **Mobile App** - Native iOS and Android applications
- [ ] **API Documentation** - Comprehensive REST API
- [ ] **Plugin System** - Extensible architecture for custom features
- [ ] **Multi-language Support** - Internationalization (i18n)
- [ ] **Advanced Reporting** - Detailed analytics and reporting tools

## 📄 License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE.md](LICENSE.md) file for details.

## 🙋‍♂️ Support & Community

- **📖 Documentation**: [Docker Deployment Guide](DOCKER_DEPLOYMENT.md)
- **🐛 Issues**: [GitHub Issues](https://github.com/PelerYuan/QuizSystem/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/PelerYuan/QuizSystem/discussions)
- **📧 Contact**: Create an issue for support requests

## 🌟 Acknowledgments

- **Flask Community** - For the amazing web framework
- **Bootstrap Team** - For the responsive UI framework
- **Chart.js Contributors** - For beautiful data visualizations
- **Docker Community** - For containerization excellence
- **All Contributors** - Thank you for making this project better!

---

<div align="center">

**Made with ❤️ for the education community**

[⭐ Star this repo](https://github.com/PelerYuan/QuizSystem) | [🐛 Report Bug](https://github.com/PelerYuan/QuizSystem/issues) | [💡 Request Feature](https://github.com/PelerYuan/QuizSystem/issues)

</div>