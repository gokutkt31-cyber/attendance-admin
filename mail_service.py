from flask_mail import Mail, Message
from flask import current_app, render_template

mail = Mail()

def send_email(subject, recipients, text_body, html_body=None):
    """
    Helper function to send email notifications.
    Fails silently in development if SMTP settings are not active.
    """
    if not recipients:
        return False
    
    try:
        msg = Message(
            subject=subject,
            recipients=recipients if isinstance(recipients, list) else [recipients],
            body=text_body,
            html=html_body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER')
        )
        mail.send(msg)
        return True
    except Exception as e:
        # Logs errors and outputs to console in development
        current_app.logger.error(f"Email failed to send to {recipients}. Error: {e}")
        print(f"--- EMAIL LOG EMULATION ---")
        print(f"To: {recipients}")
        print(f"Subject: {subject}")
        print(f"Body: {text_body}")
        print(f"---------------------------")
        return False

def send_password_reset_email(user, token):
    """
    Send password reset instructions.
    """
    # Simply using a direct url for development
    reset_url = f"http://localhost:5000/reset_password/{token}"
    subject = "Reset Your Attendance Portal Password"
    text_body = f"Hello {user.username},\n\nTo reset your password, visit the following link: {reset_url}\n\nIf you did not make this request, simply ignore this email."
    html_body = f"<p>Hello <strong>{user.username}</strong>,</p><p>To reset your password, please click the link below:</p><p><a href='{reset_url}'>{reset_url}</a></p><p>If you did not request this reset, please ignore this email.</p>"
    return send_email(subject, user.email, text_body, html_body)

def send_attendance_notification(employee, status, check_time):
    """
    Send attendance check-in/out alert emails.
    """
    subject = f"Attendance Alert: {status} registered"
    text_body = f"Hello {employee.full_name},\n\nYour attendance status [{status}] was successfully registered at {check_time}.\n\nHave a great day!"
    html_body = f"<p>Hello <strong>{employee.full_name}</strong>,</p><p>Your attendance status <strong>{status}</strong> was successfully registered at <strong>{check_time}</strong>.</p>"
    return send_email(subject, employee.email, text_body, html_body)

def send_leave_notification(employee, leave_request):
    """
    Send leave request notifications.
    """
    subject = f"Leave Request Update: {leave_request.status}"
    text_body = f"Hello {employee.full_name},\n\nYour leave application for {leave_request.start_date} to {leave_request.end_date} has been [{leave_request.status}].\n\nComments: {leave_request.comments or 'None'}"
    html_body = f"<p>Hello <strong>{employee.full_name}</strong>,</p><p>Your leave application for <strong>{leave_request.start_date} to {leave_request.end_date}</strong> has been updated to: <strong>{leave_request.status}</strong>.</p><p>Comments: {leave_request.comments or 'N/A'}</p>"
    return send_email(subject, employee.email, text_body, html_body)
