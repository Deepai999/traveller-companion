from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
import os

# Database configuration
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Use PostgreSQL on Render
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace('postgres://', 'postgresql://')
else:
    # Use SQLite for local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login page if user is not logged in

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    trips = db.relationship('Trip', backref='user', lazy=True)

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    trip_type = db.Column(db.String(50), nullable=False)
    details = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

CORS(app)

@app.route('/')
def index():
    """Serve the main HTML page"""
    return render_template('index.html')

# Structured guide data
OFFROAD_GUIDE = {
    'Driving Techniques': [
        'Lower tire pressure for better traction on sand and rocks.',
        'Use a low gear and steady throttle on steep inclines.',
        'Maintain momentum in sand and mud, but avoid spinning your wheels.',
        'When crossing water, create a gentle bow wave and avoid stopping.'
    ],
    'Safety & Recovery': [
        'Always check weather conditions before heading out.',
        'Carry recovery gear: shovel, traction boards, and a winch.',
        'Never wheel alone - use the buddy system.',
        'Know your vehicle\'s limits and your own skill level.'
    ],
    'Vehicle Preparation': [
        'Know your vehicle\'s approach, departure, and breakover angles.',
        'Secure all loose items inside and outside your vehicle.',
        'Ensure you have a full-size spare tire and the tools to change it.',
        'Pack an emergency kit with food, water, and first aid supplies.'
    ],
    'Trail Etiquette': [
        'Stay on designated trails to protect the environment.',
        'Yield to uphill traffic.',
        'Pack out everything you pack in - leave no trace.',
        'Communicate with other drivers on the trail via radio or signals.'
    ]
}

VEHICLE_CHECKS = {
    'pre_trip': [
        'Check tire pressure and condition',
        'Inspect all fluid levels',
        'Check for any leaks',
        'Test all lights',
        'Check 4WD system functionality'
    ],
    'post_trip': [
        'Inspect for any new damage',
        'Check for loose components',
        'Clean undercarriage',
        'Check fluid levels',
        'Inspect brakes'
    ]
}

@app.route('/api/guide', methods=['GET'])
def get_guide():
    """Get the complete offroad guide"""
    return jsonify(OFFROAD_GUIDE)

@app.route('/api/tips/random', methods=['GET'])
def get_random_tip():
    """Get a random offroad driving tip"""
    category = random.choice(list(OFFROAD_GUIDE.keys()))
    tip = random.choice(OFFROAD_GUIDE[category])
    return jsonify({
        'category': category,
        'tip': tip,
        'timestamp': datetime.utcnow().isoformat()
    })

def get_weather(destination):
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        return {'error': 'Weather API key not configured'}

    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': destination,
        'appid': api_key,
        'units': 'metric'  # Use metric units
    }
    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}

@app.route('/api/plan/late-night', methods=['POST'])
def plan_late_night_trip():
    """Generate a late-night offroad trip plan with weather data"""
    data = request.json
    destination = data.get('destination')

    if not destination:
        return jsonify({'error': 'Destination is required'}), 400

    weather_data = get_weather(destination)
    weather_info = {}
    trip_details = {
        'destination': destination,
        'estimated_arrival': (datetime.utcnow() + timedelta(hours=2)).isoformat(),
        'weather': {},
        'recommended_gear': ['Extra lighting', 'Warm clothing', 'Emergency blanket', 'Hot drinks'],
        'safety_notes': [
            'Be extra cautious of wildlife at night',
            'Ensure all lights are working properly',
            'Share your route with someone',
            'Take regular breaks to avoid fatigue'
        ]
    }

    if 'error' not in weather_data:
        main = weather_data.get('main', {})
        wind = weather_data.get('wind', {})
        weather = weather_data.get('weather', [{}])[0]
        weather_info = {
            'temperature': f"{main.get('temp')}°C",
            'feels_like': f"{main.get('feels_like')}°C",
            'description': weather.get('description'),
            'wind_speed': f"{wind.get('speed')} m/s"
        }
        trip_details['weather'] = weather_info

    if current_user.is_authenticated:
        new_trip = Trip(user_id=current_user.id, trip_type='late-night', details=trip_details)
        db.session.add(new_trip)
        db.session.commit()

    return jsonify(trip_details)

@app.route('/api/plan/spontaneous', methods=['POST'])
def plan_spontaneous_trip():
    """Generate a dynamic spontaneous offroad trip plan"""
    data = request.json
    duration_hours = int(data.get('duration_hours', 4))

    # Expanded list of potential activities
    all_activities = [
        'Explore a scenic viewpoint',
        'Tackle a light offroad trail',
        'Have a picnic at a scenic spot',
        'Go for a short hike',
        'Practice recovery techniques',
        'Photograph the landscape',
        'Identify local flora and fauna',
        'Test your vehicle articulation on an obstacle'
    ]

    # Determine number of activities based on duration
    num_activities = min(len(all_activities), max(1, duration_hours // 2))
    suggested_activities = random.sample(all_activities, num_activities)

    trip_details = {
        'duration_hours': duration_hours,
        'suggested_activities': suggested_activities,
        'notes': 'Enjoy your spontaneous adventure! Remember to check local conditions.'
    }

    if current_user.is_authenticated:
        new_trip = Trip(user_id=current_user.id, trip_type='spontaneous', details=trip_details)
        db.session.add(new_trip)
        db.session.commit()

    return jsonify(trip_details)

MAINTENANCE_SCHEDULE = {
    'desert': ['Check air filter', 'Inspect cooling system', 'Bring extra water for the vehicle'],
    'mountains': ['Check brakes', 'Inspect tires for rock damage', 'Test 4-low gear'],
    'mud': ['Check for differential breathers', 'Protect air intake', 'Prepare for extensive cleaning post-trip'],
    'general': ['Change oil every 3000-5000 miles', 'Rotate tires every 5000-7500 miles', 'Inspect brake pads every 10000 miles']
}

@app.route('/api/vehicle/checklist', methods=['GET'])
def get_vehicle_checklist():
    """Get vehicle maintenance checklist"""
    return jsonify(VEHICLE_CHECKS)

@app.route('/api/maintenance/anticipate', methods=['POST'])
def anticipate_maintenance():
    """Anticipate maintenance needs based on trip and mileage"""
    data = request.json
    trip_type = data.get('trip_type', 'general').lower()
    mileage = int(data.get('mileage', 0))

    recommendations = MAINTENANCE_SCHEDULE.get(trip_type, [])

    # Mileage-based recommendations
    if mileage > 0:
        if mileage % 3000 < 1000: # Nearing a 3k interval
            recommendations.append('Consider an oil change soon.')
        if mileage % 5000 < 1000: # Nearing a 5k interval
            recommendations.append('Consider rotating tires soon.')

    if not recommendations:
        recommendations = MAINTENANCE_SCHEDULE['general']

    return jsonify({
        'trip_type': trip_type,
        'mileage': mileage,
        'recommendations': recommendations
    })

MECHANIC_ASSIST = {
    'flat tire': {
        'tools': ['Jack', 'Lug wrench', 'Full-size spare tire', 'Wheel chocks'],
        'steps': [
            'Find a level, stable surface.',
            'Chock the wheels on the opposite side of the flat.',
            'Loosen the lug nuts before jacking up the vehicle.',
            'Lift the vehicle, remove the lug nuts, and replace the tire.',
            'Hand-tighten lug nuts, lower the vehicle, and then fully tighten in a star pattern.'
        ],
        'follow_up': 'Get the flat tire repaired or replaced as soon as possible. Check the spare tire pressure.'
    },
    'overheating': {
        'tools': ['Coolant', 'Water', 'Gloves'],
        'steps': [
            'Pull over safely and turn off the engine.',
            'Turn on the heater to full blast to draw heat away from the engine.',
            'DO NOT open the radiator cap while the engine is hot.',
            'After it cools (30-60 mins), check the coolant level and add more if needed.',
            'Check for visible leaks in the cooling system hoses.'
        ],
        'follow_up': 'Have your cooling system inspected by a mechanic for leaks or blockages.'
    },
    'stuck': {
        'tools': ['Shovel', 'Traction boards', 'Winch (if equipped)', 'Tire pressure gauge'],
        'steps': [
            'Assess the situation. Do not spin your wheels, as this will dig you in deeper.',
            'Clear any obstructions from around the tires and undercarriage.',
            'Lower tire pressure to 15-20 PSI for better traction.',
            'Use traction boards in front of the drive wheels.',
            'If using a winch, ensure a secure anchor point and use a damper on the line.'
        ],
        'follow_up': 'Re-inflate tires to normal pressure once back on a hard surface. Clean the undercarriage.'
    },
    'battery dead': {
        'tools': ['Jumper cables' or 'Jump starter pack'],
        'steps': [
            'Connect the red clamp to the positive (+) terminal of the dead battery.',
            'Connect the other red clamp to the positive (+) terminal of the good battery.',
            'Connect the black clamp to the negative (-) terminal of the good battery.',
            'Connect the final black clamp to an unpainted metal surface on the dead vehicle\'s frame.',
            'Start the working vehicle, wait a few minutes, then try to start the dead vehicle.'
        ],
        'follow_up': 'Let the vehicle run for at least 15-20 minutes to charge the battery. Have the battery and alternator tested.'
    }
}

@app.route('/api/mechanic/assist', methods=['POST'])
def mechanic_assistant():
    """Get detailed assistance for common vehicle issues"""
    issue = request.json.get('issue', '').lower()
    
    solution = MECHANIC_ASSIST.get(issue)
    
    if not solution:
        return jsonify({
            'issue': issue,
            'error': 'Solution not found. For serious issues, contact a professional.',
            'emergency_contact': 'Local offroad recovery: 1-800-OFF-ROAD'
        }), 404

    return jsonify({
        'issue': issue,
        'solution': solution
    })

@app.route('/api/trips', methods=['GET'])
@login_required
def get_saved_trips():
    trips = Trip.query.filter_by(user_id=current_user.id).order_by(Trip.timestamp.desc()).all()
    return jsonify([{
        'id': trip.id,
        'trip_type': trip.trip_type,
        'details': trip.details,
        'timestamp': trip.timestamp.isoformat()
    } for trip in trips])

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists.')
            return redirect(url_for('register'))
        new_user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'))
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=True)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check username and password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.cli.command('init-db')
def init_db_command():
    """Initializes the database."""
    with app.app_context():
        db.create_all()
    print('Initialized the database.')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
