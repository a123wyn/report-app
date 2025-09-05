# AI Report Generator - Amazon Q Integration

A Flask web application that generates intelligent reports using Amazon Q AI analysis, with automatic email distribution.

## 🚀 New Features

- **Amazon Q Integration**: Uses AWS Bedrock and Claude AI for intelligent data analysis
- **Smart Template Processing**: Jinja2 template engine for custom report formatting
- **AI-Powered Insights**: Generates actionable recommendations and trend analysis
- **Professional PDF Reports**: Enhanced PDF generation with AI analysis
- **Automatic Email Distribution**: Send reports to multiple recipients via Outlook

## 📋 Prerequisites

1. **AWS Account**: You need AWS credentials configured for Bedrock access
2. **AWS CLI**: Install and configure with your credentials
3. **Python 3.8+**: Required for the application
4. **Outlook Email**: For email functionality (optional)

## ⚙️ Setup Instructions

### 1. Configure AWS Credentials
```bash
aws configure
# Enter your AWS Access Key ID, Secret Access Key, and region (us-east-1 recommended)
```

### 2. Update Email Configuration
Edit `config.py` and update your email settings:
```python
EMAIL_CONFIG = {
    'sender_email': 'your-email@outlook.com',
    'sender_password': 'your-app-password',  # Use app password, not regular password
}
```

### 3. Install and Run
```bash
cd report-app
./run.sh
```

Or manually:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## 📊 Usage

1. **Access the app**: Open `http://localhost:5000`
2. **Upload files**:
   - **HTML Template**: Use Jinja2 syntax (see `sample_ai_template.html`)
   - **Markdown Prompt**: Analysis instructions (see `sample_prompt.md`)
   - **Data File**: Excel (.xlsx) or CSV file (see `sample_data.xlsx`)
3. **Add email recipients**: Comma-separated email addresses (optional)
4. **Generate Report**: Click the button to create AI-powered PDF report

## 📁 Sample Files

The app includes sample files to get you started:

- `sample_ai_template.html` - HTML template with Jinja2 syntax
- `sample_prompt.md` - Analysis instructions for Amazon Q
- `sample_data.xlsx` - Sample sales data (100 records)

## 🔧 Template Syntax

Your HTML template can use these variables:

```html
<!-- AI Analysis -->
{{ ai_analysis }}

<!-- Data Array -->
{% for row in data %}
    {% for cell in row %}
        {{ cell }}
    {% endfor %}
{% endfor %}

<!-- Data Statistics -->
Total Records: {{ data|length - 1 }}
Columns: {{ data[0]|length if data else 0 }}
```

## 🤖 AI Analysis Features

Amazon Q provides:
- **Data Overview**: Structure and quality assessment
- **Key Insights**: Trends, patterns, and anomalies
- **Business Implications**: Performance analysis
- **Actionable Recommendations**: Prioritized next steps
- **Statistical Analysis**: Relevant metrics and calculations

## 🔒 Security Notes

- Store AWS credentials securely (use IAM roles in production)
- Use app passwords for email authentication
- Keep sensitive data in environment variables
- Regularly rotate access keys

## 🛠️ Troubleshooting

### AWS Issues
- Ensure Bedrock is available in your region (us-east-1 recommended)
- Check IAM permissions for Bedrock access
- Verify AWS credentials: `aws sts get-caller-identity`

### Email Issues
- Use app-specific passwords for Outlook
- Enable 2FA and generate app password in Microsoft account settings
- Check firewall settings for SMTP (port 587)

### File Upload Issues
- Maximum file size: 100MB
- Supported formats: .xlsx, .csv, .html, .md
- Ensure files are not corrupted

## 📈 Performance

- Processes up to 10,000 rows efficiently
- PDF generation optimized for large datasets
- AI analysis typically takes 10-30 seconds
- Email delivery is asynchronous

## 🔄 Updates

The app now includes:
- Enhanced error handling
- Better PDF formatting
- Improved AI prompts
- Professional email templates
- Sample data generation

Access the application at: `http://localhost:5000`
