# AI Healthcare Scheduling Agent

A production-ready AI-powered scheduling agent for healthcare clinics that automates patient booking, reduces no-shows, and streamlines clinic operations.

## 🎯 Features

### Core Functionality
- **Patient Greeting & Intake**: Collects and validates patient information using NLP
- **Patient Lookup**: Maintains synthetic patient database with 50 entries
- **Smart Scheduling**: 60min slots for new patients, 30min for returning patients
- **Calendar Integration**: Excel-based availability management
- **Insurance Collection**: Captures carrier, member ID, and group number
- **Appointment Confirmation**: Exports to Excel and sends confirmations
- **Form Distribution**: Emails New Patient Intake Form after confirmation
- **Reminder System**: 3 automated reminders (simple, forms, confirmation)

### Technical Features
- **LangGraph + LangChain**: Multi-agent orchestration
- **Streamlit Frontend**: Interactive chatbot interface
- **Email & SMS Integration**: Gmail SMTP + Twilio
- **Excel Export**: Admin reports and data management
- **Modular Architecture**: Scalable and maintainable design

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ReceptionAutomation
   ```

2. **Create virtual environment**
   ```bash
   python -m venv clinic_env
   clinic_env\Scripts\activate  # Windows
   # or
   source clinic_env/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate synthetic data**
   ```bash
   python data_generator.py
   ```

5. **Configure environment variables**
   ```bash
   copy env_example.txt .env
   # Edit .env with your API keys
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 📁 Project Structure

```
ReceptionAutomation/
├── app.py                      # Streamlit frontend
├── ai_agent.py                 # LangGraph AI agent
├── config.py                   # Configuration settings
├── data_generator.py           # Synthetic data generation
├── database.py                 # Database management
├── patient_intake.py           # Patient information collection
├── insurance_collection.py     # Insurance data handling
├── scheduling.py               # Smart scheduling logic
├── messaging.py                # Email and SMS services
├── reminder_system.py          # Automated reminders
├── requirements.txt            # Python dependencies
├── env_example.txt             # Environment variables template
├── technical_approach.md       # Technical documentation
├── README.md                   # This file
├── data/                       # Generated data files
│   ├── patients.csv
│   ├── doctors.csv
│   ├── doctor_schedules.xlsx
│   └── appointments.csv
└── resources/                  # Static resources
    └── New Patient Intake Form.pdf
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file with the following variables:

```env
# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USERNAME=your_email@gmail.com
EMAIL_PASSWORD=your_app_password

# Twilio SMS Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number

# OpenAI API (for LangChain)
OPENAI_API_KEY=your_openai_api_key

# Database Configuration
DATABASE_URL=sqlite:///clinic_scheduling.db
```

### Gmail Setup
1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password for the application
3. Use the App Password in the EMAIL_PASSWORD variable

### Twilio Setup
1. Create a Twilio account
2. Get your Account SID and Auth Token
3. Purchase a phone number for SMS
4. Add the credentials to your .env file

## 🏥 Usage

### Chat Interface
1. Open the Streamlit app in your browser
2. Use the "Chat Interface" tab to interact with the AI agent
3. Follow the conversation flow to schedule appointments
4. The agent will guide you through:
   - Patient information collection
   - Insurance details
   - Appointment scheduling
   - Confirmation and form distribution

### Dashboard
- View clinic statistics and metrics
- Monitor appointment trends
- Track doctor workload
- Review recent appointments

### Admin Panel
- Send manual reminders
- Generate reports
- Export data
- Manage appointments

## 📊 Data Management

### Synthetic Data
The system includes:
- **50 Patient Records**: Realistic demographic data
- **3 Doctors**: Specialized in different areas
- **30-day Schedule**: Available appointment slots
- **Insurance Coverage**: Multiple carriers and plans

### Data Export
- **CSV Format**: Easy import/export
- **Excel Integration**: Professional reporting
- **Real-time Updates**: Immediate availability checking

## 🔧 Development

### Adding New Features
1. **New Agent Nodes**: Add to LangGraph workflow in `ai_agent.py`
2. **New Services**: Create modular services following existing patterns
3. **New Validations**: Add to appropriate validation classes
4. **New Integrations**: Extend messaging or database services

### Testing
```bash
# Run data generator to create test data
python data_generator.py

# Test individual components
python -c "from database import PatientDatabase; db = PatientDatabase(); print('Database loaded successfully')"
```

### Debugging
- Check Streamlit logs in the terminal
- Review conversation state in the chat interface
- Export chat history for analysis
- Use the admin panel to inspect data

## 📈 Performance

### Optimization Features
- **Streamlit Caching**: Reduces database load
- **Session State**: Maintains conversation context
- **File-based Storage**: No database bottlenecks
- **Modular Architecture**: Independent service scaling

### Scalability
- **Stateless Design**: Easy horizontal scaling
- **File-based Storage**: No database dependencies
- **Modular Services**: Independent scaling
- **Configuration-based**: Easy deployment

## 🛡️ Security

### Data Protection
- **Environment Variables**: No hardcoded secrets
- **Input Validation**: Prevents injection attacks
- **Session Isolation**: User data separation
- **Error Handling**: Graceful failure recovery

### HIPAA Compliance (Future)
- **Encryption**: Data encryption at rest and in transit
- **Audit Logging**: Complete activity tracking
- **Access Controls**: Role-based permissions
- **Data Retention**: Configurable policies

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Deployment
1. **Server Setup**: Deploy to cloud provider (AWS, Azure, GCP)
2. **Environment Configuration**: Set production environment variables
3. **SSL Certificate**: Enable HTTPS for secure communication
4. **Monitoring**: Set up logging and monitoring
5. **Backup Strategy**: Regular data backups

### Docker Deployment (Optional)
```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

## 📞 Support

### Troubleshooting
1. **Check Environment Variables**: Ensure all required variables are set
2. **Verify Dependencies**: Run `pip install -r requirements.txt`
3. **Check Data Files**: Ensure data directory exists with required files
4. **Review Logs**: Check terminal output for error messages

### Common Issues
- **Import Errors**: Ensure virtual environment is activated
- **Email Issues**: Check Gmail App Password configuration
- **SMS Issues**: Verify Twilio credentials and phone number
- **Data Issues**: Regenerate data with `python data_generator.py`

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📚 Documentation

- **Technical Approach**: See `technical_approach.md` for detailed architecture
- **API Documentation**: Check individual module docstrings
- **User Guide**: Follow the chat interface for usage examples

## 🎯 Roadmap

### Phase 2
- Real EMR integration
- Advanced analytics
- Mobile app
- Voice integration

### Phase 3
- AI-powered recommendations
- Predictive analytics
- Multi-language support
- Advanced reporting

---

**Built with ❤️ for healthcare automation**

