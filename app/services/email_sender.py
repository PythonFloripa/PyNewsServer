import resend

resend = resend.Resend(os.getenv("RESEND_API_KEY"))

def send_email(to: str, subject: str, body: str):
    resend.emails.send(
        from="onboarding@resend.dev",
        to=to,
        subject=subject,
        html=body,
    )
