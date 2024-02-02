from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import show_db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///coords.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class CreatingFont(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    font_name = db.Column(db.String(50), nullable=False)
    letter = db.Column(db.String(1), nullable=False)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    new_line = db.Column(db.Boolean, nullable=False, default=False)

class TextSamples(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    font_name = db.Column(db.String(50), nullable=False)
    text_sample = db.Column(db.Integer, nullable=False)
    x = db.Column(db.Integer, nullable=False)
    y = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    new_line = db.Column(db.Boolean, nullable=False, default=False)

def create_table_if_not_exists():
    if not db.inspect(db.engine).has_table('CreatingFont'):
        with app.app_context():
            db.create_all()
    if not db.inspect(db.engine).has_table('TextSamples'):
        with app.app_context():
            db.create_all()


@app.route('/mouse_tracking/text_input')
def textinput():
    return render_template('textInput.html')

@app.route('/mouse_tracking')
def tracking():
    return render_template('mouse.html')

@app.route('/save', methods=['POST'])
def save_coordinates():
    data = request.json
    # print("Received data:", data)  # Debug-Ausgabe
    font_name = data['font_name']
    letter = data['letter']
    if ord(letter) == 8220:
        letter = chr(34)
    points = data['points']

    create_table_if_not_exists()

    for i, point in enumerate(points):
        x = point['x']
        y = point['y']
        isNewLine = point.get('isNewLine', False) # isNewLine aus dem Punkt abrufen (Standardwert ist False)
        
        new_drawing = CreatingFont(font_name=font_name, letter=letter, x=x, y=y, new_line=isNewLine)
        db.session.add(new_drawing)
    db.session.commit()

    return jsonify({'message': 'Koordinaten gespeichert'})

@app.route('/saveText', methods=['POST'])
def save_coordinates_Text():
    data = request.json
    # print("Received data:", data)  # Debug-Ausgabe
    font_name = data['font_name']
    text_sample = data['text_sample']
    points = data['points']

    create_table_if_not_exists()

    for i, point in enumerate(points):
        x = point['x']
        y = point['y']
        isNewLine = point.get('isNewLine', False) # isNewLine aus dem Punkt abrufen (Standardwert ist False)
        
        new_textInput = TextSamples(font_name=font_name, text_sample=text_sample, x=x, y=y, new_line=isNewLine)
        db.session.add(new_textInput)
    db.session.commit()
    return jsonify({'message': 'Koordinaten gespeichert'})

@app.route('/tracked_letters', methods=['GET'])
def tracked_letters():
    font_name_input = request.args.get('font_name', '')  # Get the font name from the query string
    tracked_letters = db.session.query(CreatingFont.letter).filter_by(font_name=font_name_input).distinct().all()
    tracked_letters = [letter[0] for letter in tracked_letters]
    print(tracked_letters)
    return jsonify(tracked_letters)


@app.route('/create_plot', methods=['GET'])
def create_plot():
    font_name = request.args.get('font_name')

    plot_path = show_db.main(font_name)

    # Annahme: plot_path enthält den Pfad zum generierten Plot
    return jsonify({'plot_path': plot_path})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host="0.0.0.0")