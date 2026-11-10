from flask import Flask, render_template_string, request

app = Flask(__name__)

# Simple HTML template containing the form and result display
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Comment Submission</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 40px auto; padding: 20px; }
        textarea { width: 100%; height: 100px; margin-bottom: 10px; }
        .comment-box { background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin-top: 20px; }
    </style>
</head>
<body>
    <h2>Leave a Comment</h2>
    <form method="POST" action="/">
        <textarea name="comment" placeholder="Type your comment here..." required></textarea><br>
        <button type="submit">Submit</button>
    </form>

    {% if comment %}
        <div class="comment-box">
            <h3>Your Submitted Comment:</h3>
            <p>{{ comment }}</p>
        </div>
    {% endif %}
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
    user_comment = None
    if request.method == "POST":
        # Extract comment from the form payload
        user_comment = request.form.get("comment")

    return render_template_string(HTML_TEMPLATE, comment=user_comment)


if __name__ == "__main__":
    app.run(debug=True)