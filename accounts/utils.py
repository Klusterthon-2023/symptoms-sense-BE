# accounts.utils

from django.core.mail.message import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings

# Send email for registration, resets
def send_multi_format_email(template_prefix, template_ctxt, target_email):
    subject_file = 'accounts/%s_subject.txt' % template_prefix
    txt_file = 'accounts/%s.txt' % template_prefix
    html_file = 'accounts/%s.html' % template_prefix

    subject = render_to_string(subject_file).strip()
    from_email = settings.EMAIL_FROM
    to = target_email
    # bcc_email = settings.EMAIL_BCC
    text_content = render_to_string(txt_file, template_ctxt)
    html_content = render_to_string(html_file, template_ctxt)
    msg = EmailMessage(subject, html_content, from_email, [to])
    # msg.attach_alternative(text_content, 'text/plain')
    msg.content_subtype = "html"
    msg.send()
