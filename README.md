# GDP Analytics - University Project

A comprehensive web application for analyzing global economic and social indicators with interactive visualizations, machine learning capabilities, and geographic analysis.

## 🎓 **University of Helsinki - GDP Analytics Project**

### **Features**
- 📊 **Interactive Data Explorer** - Browse 12 social indicators across 250+ countries
- 📈 **Dynamic Visualizations** - Real-time charts with filtering capabilities  
- 🗺️ **Geographic Analysis** - Blog with interactive maps and research insights
- 🤖 **ML Model Experimentation** - Compare different prediction models
- 🏛️ **Country Profiles** - Detailed analysis for individual countries
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile

### **Data Coverage**
- **250+ Countries** worldwide
- **12 Social Indicators**: GDP, Population, Life Expectancy, Internet Penetration, Human Capital Index, and more
- **Time Period**: 1960-2023 (60+ years of historical data)
- **8,398 Data Records** with comprehensive coverage

### **Technology Stack**
- **Backend**: Python Flask with SQLite database
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Visualizations**: Plotly.js, Matplotlib, Seaborn
- **Maps**: Geopandas, Folium for geographic analysis
- **ML**: Scikit-learn for model experimentation

## 🚀 **Quick Start**

### **Local Development**
```bash
# Clone the repository
git clone https://github.com/yourusername/gdp-analytics-project.git
cd gdp-analytics-project

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Visit http://127.0.0.1:5000
```

### **Production Deployment**
Ready for deployment on Railway, Heroku, Vercel, or any Python hosting platform.

```bash
# Production build
pip install -r requirements-production.txt
gunicorn wsgi:application
```

## 📁 **Project Structure**
```
GDP Project/
├── app.py                      # Main Flask application
├── wsgi.py                     # Production WSGI entry point
├── database_crud.py            # Database operations
├── config.py                   # Application configuration
├── model_experiments.py        # ML experimentation module
├── database/
│   └── data.db                 # SQLite database with GDP data
├── templates/                  # HTML templates
├── static/                     # CSS, JavaScript, images
├── logs/                       # Application logs
└── requirements*.txt           # Dependencies
```

## 🎯 **Key Pages**

### **Data Explorer** (`/data`)
- Browse all 12 social indicators
- Filter by country, year, and metric
- Export data functionality
- Detailed country profiles

### **Visualizations** (`/visualizations`)  
- Interactive charts (Bar, Line, Scatter, Histogram)
- Real-time filtering and updates
- Professional data presentation

### **Geographic Analysis** (`/blog`)
- Interactive world maps
- Research insights and analysis
- University-quality content

### **ML Models** (`/ml_models`)
- Model experimentation interface
- Compare Linear Regression vs LightGBM
- Feature impact analysis
- Academic research tools

## 🎓 **Academic Features**
- Professional University of Helsinki branding
- Research-quality visualizations  
- Academic presentation suitable for coursework
- Export capabilities for reports and presentations
- Comprehensive data analysis tools

## 📊 **Available Social Indicators**

### **Economic Indicators**
- GDP per Capita (USD)
- Total Population
- Net Migration

### **Health & Demographics**  
- Life Expectancy (Years)
- Infant Mortality Rate (per 1,000 births)
- Female/Male Population Distribution (%)

### **Technology & Development**
- Internet Penetration (%)
- Human Capital Index (0-1 scale)
- School Enrollment (%)
- Urban Population (%)

## 🔧 **Development**

### **Database**
SQLite database with comprehensive GDP and social indicator data:
- Optimized for web application use
- Includes data validation and preprocessing
- Ready for analysis and visualization

### **Configuration**
- Development and production configurations
- Environment-based settings
- Logging system with multiple log levels

### **Testing**
```bash
# Run tests
python test_charts.py
python test_time.py
```

## 🌐 **Deployment Options**

### **Railway.app (Recommended)**
- Free tier with generous limits
- Automatic deployment from GitHub
- Perfect for Python/Flask applications

### **Other Platforms**
- Heroku (traditional choice)
- Vercel (serverless)
- PythonAnywhere (Python-focused)
- DigitalOcean App Platform

See `HOSTING_GUIDE.md` for detailed deployment instructions.

## 📖 **Documentation**
- `HOSTING_GUIDE.md` - Complete deployment guide
- `DATA_EXPLORER_ENHANCEMENT.md` - Feature documentation
- `VISUALIZATION_ENHANCEMENT.md` - UI improvements
- `MODELEXP_IMPLEMENTATION.md` - ML experimentation guide

## 🎯 **University Project Goals**
This application demonstrates:
- Full-stack web development skills
- Data analysis and visualization capabilities
- Machine learning implementation
- Professional software deployment
- Academic research presentation

## 📄 **License**
This project is created for academic purposes at the University of Helsinki.

## 👨‍💼 **Author**
University of Helsinki Student Project
- Course: [Your Course Name]
- Semester: [Your Semester]
- Year: 2025

---

**Live Demo**: [Your deployed URL will go here]

**Contact**: [Your university email]