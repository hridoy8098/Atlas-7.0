import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailManager:
    def __init__(self, smtp_server=None, smtp_port=None, username=None, password=None):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port or 587
        self.username = username
        self.password = password
        self.templates = {}
        self._load_templates()

    def _get_templates_path(self):
        return os.path.join(os.path.dirname(__file__), "email_templates.json")

    def _load_templates(self):
        path = self._get_templates_path()
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    self.templates = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.templates = {}

    def _save_templates(self):
        path = self._get_templates_path()
        with open(path, "w") as f:
            json.dump(self.templates, f, indent=2)

    def create_template(self, name, subject, body_text, body_html=""):
        self.templates[name] = {
            "subject": subject,
            "body_text": body_text,
            "body_html": body_html,
        }
        self._save_templates()

    def get_template(self, name):
        template = self.templates.get(name)
        if not template:
            raise KeyError(f"Template '{name}' not found")
        return template

    def list_templates(self):
        return list(self.templates.keys())

    def delete_template(self, name):
        if name not in self.templates:
            raise KeyError(f"Template '{name}' not found")
        del self.templates[name]
        self._save_templates()

    def compose_email(self, to_addr, subject, body_text, body_html="", cc_addr=None, bcc_addr=None, template_name=None):
        if template_name:
            template = self.get_template(template_name)
            subject = template["subject"]
            body_text = template["body_text"]
            body_html = template["body_html"]

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = self.username or ""
        msg["To"] = to_addr
        if cc_addr:
            msg["Cc"] = cc_addr
        msg.attach(MIMEText(body_text, "plain"))
        if body_html:
            msg.attach(MIMEText(body_html, "html"))

        recipients = [to_addr]
        if cc_addr:
            recipients.append(cc_addr)
        if bcc_addr:
            recipients.append(bcc_addr)

        return {"message": msg, "recipients": recipients, "subject": subject, "body": body_text}

    def send_email(self, to_addr, subject, body_text, body_html="", cc_addr=None, bcc_addr=None):
        composed = self.compose_email(to_addr, subject, body_text, body_html, cc_addr, bcc_addr)
        if not self.smtp_server or not self.username:
            raise ConnectionError("SMTP server and username not configured")
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password or "")
            server.sendmail(self.username, composed["recipients"], composed["message"].as_string())
        return {"status": "sent", "to": to_addr, "subject": subject}

    def send_template_email(self, template_name, to_addr, cc_addr=None, bcc_addr=None):
        template = self.get_template(template_name)
        return self.send_email(
            to_addr=to_addr,
            subject=template["subject"],
            body_text=template["body_text"],
            body_html=template["body_html"],
            cc_addr=cc_addr,
            bcc_addr=bcc_addr,
        )
