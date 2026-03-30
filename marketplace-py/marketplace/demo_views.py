from django.shortcuts import render, redirect
from django.http import HttpResponse

from audio.models import AudioSnippet
from jobs.models import Job, JobApplication, JobSubmission
from users.models import User

DEMO_PASSWORD = "accessovox"
SESSION_KEY = "demo_guide_authed"


def demo_guide(request):
    """Password-protected demo guide page."""
    # Check if already authenticated via session
    if not request.session.get(SESSION_KEY):
        # Check for password submission
        if request.method == "POST":
            if request.POST.get("password") == DEMO_PASSWORD:
                request.session[SESSION_KEY] = True
            else:
                return _render_login(request, error=True)
        else:
            return _render_login(request)

    # Gather stats
    languages = set()
    for u in User.objects.values_list("native_languages", flat=True):
        if u:
            for lang in u.split(","):
                lang = lang.strip()
                if lang and lang != "es":
                    languages.add(lang)

    context = {
        "user_count": User.objects.count(),
        "job_count": Job.objects.count(),
        "app_count": JobApplication.objects.count(),
        "sub_count": JobSubmission.objects.count(),
        "language_count": len(languages),
        "audio_count": AudioSnippet.objects.count()
        + JobSubmission.objects.exclude(audio_file="")
        .exclude(audio_file__isnull=True)
        .count()
        + User.objects.exclude(profile_audio="")
        .exclude(profile_audio__isnull=True)
        .count(),
    }
    return render(request, "demo_guide.html", context)


def _render_login(request, error=False):
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Demo Guide</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
        }
        .box {
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 2.5rem;
            width: 100%;
            max-width: 380px;
            text-align: center;
        }
        h1 {
            font-size: 1.25rem;
            font-weight: 300;
            margin-bottom: 1.5rem;
            color: #f8fafc;
        }
        h1 strong { color: #38bdf8; font-weight: 700; }
        input[type="password"] {
            width: 100%;
            padding: 0.75rem 1rem;
            background: #0f172a;
            border: 1px solid #334155;
            border-radius: 8px;
            color: #f8fafc;
            font-size: 1rem;
            text-align: center;
            letter-spacing: 0.1em;
            margin-bottom: 1rem;
        }
        input:focus {
            outline: 2px solid #38bdf8;
            border-color: #38bdf8;
        }
        button {
            width: 100%;
            padding: 0.75rem;
            background: #38bdf8;
            color: #0f172a;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 700;
            cursor: pointer;
        }
        button:hover { background: #7dd3fc; }
        .error {
            color: #f87171;
            font-size: 0.85rem;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <div class="box">
        <h1><strong>Demo Guide</strong></h1>
        """ + ('<p class="error">Wrong password.</p>' if error else '') + """
        <form method="post">
            <input type="hidden" name="csrfmiddlewaretoken" value="{csrf}">
            <input type="password" name="password" placeholder="Password" autofocus>
            <button type="submit">Enter</button>
        </form>
    </div>
</body>
</html>"""
    from django.middleware.csrf import get_token

    html = html.replace("{csrf}", get_token(request))
    return HttpResponse(html)
