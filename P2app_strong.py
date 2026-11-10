from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/", methods=["GET"])
def index():
    return render_template("comment.html")


@app.route("/comment", methods=["POST"])
def submit_comment():
    user_comment = request.form.get("comment", "")
    return render_template("comment.html", comment=user_comment)


if __name__ == "__main__":
    app.run(debug=False)