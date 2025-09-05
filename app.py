from flask import Flask, render_template, request, send_file, flash, redirect, url_for, session, Response
import csv
import openpyxl
import markdown
import os
import json
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from werkzeug.utils import secure_filename
from jinja2 import Template
import html
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 基本认证
def check_auth(username, password):
    return (username == os.environ.get('AUTH_USERNAME', 'admin') and 
            password == os.environ.get('AUTH_PASSWORD', 'demo123'))

def authenticate():
    return Response('需要登录', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

# Q CLI integration - no AWS credentials needed
def call_amazon_q(prompt, data_context):
    """Call Amazon Q via CLI to generate intelligent report content"""
    try:
        # Prepare the full prompt
        full_prompt = f"""
Based on the following data and instructions, generate a comprehensive report:

Instructions: {prompt}

Data Context: {json.dumps(data_context, indent=2)}

Please generate a detailed analysis and report based on this data and the provided instructions.
Focus on key insights, trends, and actionable recommendations.
"""
        
        # Use Q CLI to generate response
        result = subprocess.run(
            ['q', 'chat', '--no-interactive', full_prompt],
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=60
        )
        
        if result.returncode == 0:
            # Clean up the response text
            response_text = result.stdout.strip()
            # Remove any control characters that might cause issues
            response_text = ''.join(char for char in response_text if ord(char) >= 32 or char in '\n\r\t')
            return response_text
        else:
            return f"Q CLI error: {result.stderr}"
            
    except subprocess.TimeoutExpired:
        return "Amazon Q request timed out. Using fallback content generation."
    except FileNotFoundError:
        return "Q CLI not found. Please install Amazon Q CLI first."
    except Exception as e:
        return f"Error calling Amazon Q: {str(e)}"
        
        # Use Claude via Bedrock
        response = bedrock_client.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 4000,
                'messages': [
                    {
                        'role': 'user',
                        'content': full_prompt
                    }
                ]
            })
        )
        
        response_body = json.loads(response['body'].read())
        return response_body['content'][0]['text']
        
    except Exception as e:
        print(f"Amazon Q call failed: {e}")
        return f"AI Analysis: Based on the provided data and instructions, here's a summary of the key findings and insights from the dataset."

def process_template_with_data(template_content, data, ai_analysis):
    """Process HTML template with data using Jinja2"""
    try:
        template = Template(template_content)
        return template.render(data=data, ai_analysis=ai_analysis)
    except Exception as e:
        print(f"Template processing error: {e}")
        return f"<h1>Report</h1><p>{ai_analysis}</p>"

@app.route('/')
@requires_auth
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_report():
    try:
        email_list = request.form.get('email_list', '').strip()
        emails = [email.strip() for email in email_list.split(',') if email.strip()]
        
        template_file = request.files.get('template_file')
        prompt_file = request.files.get('prompt_file')
        data_file = request.files.get('data_file')
        
        if not all([template_file, prompt_file, data_file]):
            flash('Error: All three files (template HTML, prompt MD, data Excel/CSV) must be uploaded')
            return redirect(url_for('index'))
        
        # Validate file extensions
        if not template_file.filename.lower().endswith(('.html', '.htm')):
            flash('Error: Template file must be HTML format')
            return redirect(url_for('index'))
        
        if not prompt_file.filename.lower().endswith('.md'):
            flash('Error: Prompt file must be Markdown (.md) format')
            return redirect(url_for('index'))
        
        if not data_file.filename.lower().endswith(('.xlsx', '.csv')):
            flash('Error: Data file must be Excel (.xlsx) or CSV format')
            return redirect(url_for('index'))
        
        # Save uploaded files - STRICTLY using user-uploaded files only, no sample files
        template_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(template_file.filename))
        prompt_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(prompt_file.filename))
        data_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(data_file.filename))
        
        template_file.save(template_path)
        prompt_file.save(prompt_path)
        data_file.save(data_path)
        
        # Read ONLY the uploaded files - no fallback to sample data
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
        
        # Process data file
        data = read_data_file(data_path, data_file.filename)
        data_context = prepare_data_context(data)
        
        # Call Amazon Q for intelligent analysis
        ai_analysis = call_amazon_q(prompt_content, data_context)
        
        # Process template with AI analysis and data
        processed_content = process_template_with_data(template_content, data, ai_analysis)
        
        # Generate HTML report instead of PDF
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'generated_report.html')
        generate_html_report(data, processed_content, ai_analysis, output_path)
        
        # Store email list for later use (optional)
        if emails:
            # Save email list to session for potential later use
            session['email_list'] = emails
            flash(f'Report generated successfully! You can send it to {len(emails)} recipients later.')
        else:
            flash('Report generated successfully with Amazon Q analysis!')
        
        return send_file(output_path, as_attachment=True, download_name='ai_generated_report.html')
        
    except Exception as e:
        flash(f'Error: {str(e)}')
        return redirect(url_for('index'))

@app.route('/send_email', methods=['POST'])
def send_email():
    try:
        email_list = request.form.get('email_list', '').strip()
        emails = [email.strip() for email in email_list.split(',') if email.strip()]
        
        if not emails:
            flash('Please provide email addresses')
            return redirect(url_for('index'))
        
        # Check if report exists
        report_path = os.path.join(app.config['UPLOAD_FOLDER'], 'generated_report.html')
        if not os.path.exists(report_path):
            flash('No report found. Please generate a report first.')
            return redirect(url_for('index'))
        
        # Send emails
        send_emails(emails, report_path)
        flash(f'Report sent successfully to {len(emails)} recipients!')
        
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Email sending failed: {str(e)}')
        return redirect(url_for('index'))

def read_data_file(file_path, filename):
    if filename.endswith('.xlsx'):
        wb = openpyxl.load_workbook(file_path)
        ws = wb.active
        data = []
        for row in ws.iter_rows(values_only=True):
            if any(cell is not None for cell in row):
                data.append([str(cell) if cell is not None else '' for cell in row])
        return data
    else:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            return [row for row in reader]

def prepare_data_context(data):
    """Prepare data context for Amazon Q analysis"""
    if not data:
        return {}
    
    # Extract headers and sample data
    headers = data[0] if data else []
    sample_rows = data[1:6] if len(data) > 1 else []  # First 5 data rows
    
    return {
        'headers': headers,
        'sample_data': sample_rows,
        'total_rows': len(data) - 1,  # Excluding header
        'columns_count': len(headers)
    }

def generate_html_report(data, processed_content, ai_analysis, output_path):
    """Generate HTML report using processed template content"""
    
    # Ensure proper encoding for AI analysis
    if isinstance(ai_analysis, bytes):
        ai_analysis = ai_analysis.decode('utf-8', errors='ignore')
    
    # Clean and format AI analysis text
    ai_analysis_clean = ai_analysis.replace('\n', '<br>\n').replace('\r', '')
    
    # Create complete HTML document with AI analysis
    full_html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>AI Generated Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .ai-analysis {{ background-color: #f0f8ff; padding: 20px; margin: 20px 0; border-left: 5px solid #007cba; border-radius: 5px; }}
        .ai-analysis h2 {{ color: #007cba; margin-top: 0; }}
        .ai-content {{ white-space: pre-wrap; word-wrap: break-word; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
        th {{ background-color: #f2f2f2; font-weight: bold; }}
        tr:nth-child(even) {{ background-color: #f9f9f9; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .timestamp {{ color: #666; font-size: 0.9em; text-align: right; margin-top: 20px; }}
    </style>
</head>
<body>
    {processed_content}
    
    <div class="ai-analysis">
        <h2>🤖 AI Analysis & Insights</h2>
        <div class="ai-content">{ai_analysis_clean}</div>
    </div>
    
    <div class="timestamp">
        Report generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
</body>
</html>"""
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

def send_emails(email_list, report_path):
    """Send emails using configured SMTP settings"""
    try:
        from email_config import EMAIL_CONFIG
        
        sender_email = EMAIL_CONFIG['sender_email']
        sender_password = EMAIL_CONFIG['sender_password']
        smtp_server = EMAIL_CONFIG['smtp_server']
        smtp_port = EMAIL_CONFIG['smtp_port']
        
        # Connect to SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        
        success_count = 0
        for recipient in email_list:
            try:
                # Create message
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = recipient
                msg['Subject'] = "AI-Generated Data Report"
                
                # Email body
                body = """Dear Recipient,

Please find the attached AI-generated report created using Amazon Q analysis.

This report includes:
- Intelligent data analysis powered by Amazon Q
- Key insights and trends from your data
- Actionable recommendations

Best regards,
Report Generation System"""
                
                msg.attach(MIMEText(body, 'plain'))
                
                # Attach HTML report
                with open(report_path, "rb") as attachment:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.read())
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename=ai_report.html'
                    )
                    msg.attach(part)
                
                # Send email
                server.send_message(msg)
                success_count += 1
                print(f"Email sent successfully to {recipient}")
                
            except Exception as e:
                print(f"Failed to send email to {recipient}: {e}")
        
        server.quit()
        
        if success_count > 0:
            return f"Successfully sent emails to {success_count} out of {len(email_list)} recipients"
        else:
            return "Failed to send any emails. Please check email configuration."
            
    except ImportError:
        return "Email configuration not found. Please update email_config.py with your email settings."
    except Exception as e:
        print(f"Email sending failed: {e}")
        return f"Email sending failed: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(debug=debug, host='0.0.0.0', port=port)
