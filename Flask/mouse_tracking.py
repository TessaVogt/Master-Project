from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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

def create_table_if_not_exists():
    if not db.inspect(db.engine).has_table('CreatingFont'):
        with app.app_context():
            db.create_all()

@app.route('/mouse_tracking')
def tracking():
    return render_template('mouse.html')

@app.route('/save', methods=['POST'])
def save_coordinates():
    data = request.json
    print("Received data:", data)  # Debug-Ausgabe
    font_name = data['font_name']
    letter = data['letter']
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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
