from flask import Flask, request, render_template_string, session, redirect, url_for
import random
import os

app = Flask(__name__)
# A secret key is required to use the session feature
app.secret_key = os.urandom(24)

# HTML template with embedded CSS for styling and Jinja2 for dynamic content
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Guess the Number</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #f0f2f5;
            color: #333;
            margin: 0;
        }
        .container {
            background: #fff;
            padding: 2rem 3rem;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
            text-align: center;
            width: 90%;
            max-width: 400px;
        }
        h1 {
            color: #1a73e8;
            margin-bottom: 0.5rem;
        }
        p {
            margin-bottom: 1.5rem;
            line-height: 1.6;
        }
        .message {
            font-size: 1.2rem;
            font-weight: 600;
            margin: 1.5rem 0;
            padding: 1rem;
            border-radius: 8px;
            color: #fff;
            background-color: {{ message_color|default('#6c757d') }}; /* Default grey */
        }
        .form-group {
            margin-bottom: 1rem;
        }
        input[type="number"] {
            width: 80%;
            padding: 0.75rem;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1.2rem;
            text-align: center;
            transition: border-color 0.2s;
        }
        input[type="number"]:focus {
            outline: none;
            border-color: #1a73e8;
        }
        .btn {
            display: inline-block;
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            font-weight: 600;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            text-decoration: none;
            transition: background-color 0.2s, transform 0.1s;
        }
        .btn:active {
            transform: translateY(1px);
        }
        .btn-primary {
            background-color: #1a73e8;
            color: #fff;
        }
        .btn-secondary {
            background-color: #e9ecef;
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎯 Guess the Number!</h1>
        <p>I’m thinking of a number between <strong>1 and 100</strong>.</p>

        {% if message %}
        <div class="message">
            {{ message|safe }}
        </div>
        {% endif %}

        <form method="POST" action="/">
            <div class="form-group">
                <input type="number" name="guess" placeholder="Enter your guess" min="1" max="100" required autofocus>
            </div>
            <button type="submit" class="btn btn-primary">Guess</button>
        </form>

        <p style="margin-top: 2rem;">
            Guesses so far: <strong>{{ session.get('guess_count', 0) }}</strong>
        </p>

        <a href="/reset" class="btn btn-secondary">🔄 Reset Game</a>
    </div>
</body>
</html>
"""

def start_new_game():
    """Initializes or resets the game state in the session."""
    session['secret_number'] = random.randint(1, 100)
    session['guess_count'] = 0
    session['message'] = "Enter a number below to start playing!"
    session['message_color'] = '#6c757d' # Grey color for initial message


@app.route('/', methods=['GET', 'POST'])
def game():
    # Start a new game if one isn't in progress
    if 'secret_number' not in session:
        start_new_game()

    if request.method == 'POST':
        # Don't process the form if the game was just won
        if 'game_won' in session:
            session.pop('game_won', None) # Clear the flag
            start_new_game()
            return redirect(url_for('game'))

        try:
            guess = int(request.form['guess'])
            secret = session.get('secret_number')
            session['guess_count'] += 1

            if guess < secret:
                session['message'] = f"🔻 Too low! Try something higher than {guess}."
                session['message_color'] = '#dc3545' # Red
            elif guess > secret:
                session['message'] = f"🔺 Too high! Try something lower than {guess}."
                session['message_color'] = '#ffc107' # Yellow
            else:
                session['message'] = f"🎉 Correct! You found the number {secret} in {session['guess_count']} guesses!"
                session['message_color'] = '#28a745' # Green
                session['game_won'] = True # Set a flag to reset on the next POST

        except (ValueError, KeyError):
            session['message'] = "🤔 Please enter a valid number."
            session['message_color'] = '#dc3545' # Red
        
        # Redirect to the same page using GET to prevent form resubmission issues
        return redirect(url_for('game'))

    # For a GET request, just render the template with the current session state
    return render_template_string(
        HTML_TEMPLATE,
        message=session.get('message'),
        message_color=session.get('message_color')
    )


@app.route('/reset')
def reset():
    """Clear session and start a new game."""
    start_new_game()
    return redirect(url_for('game'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)