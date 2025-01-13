from flask import Flask, render_template, jsonify
from traffic_light_controller import TrafficJunction
import threading
import time
from traffic_simulation import TrafficSimulation, start_simulation
import multiprocessing

app = Flask(__name__)

# Global variables to store traffic system state
current_state = {
    'active_lane': 0,
    'timer': 0,
    'light_status': 'RED',
    'density': 0,
    'is_running': False
}

# Initialize traffic junction
lanes = [
    {
        'current': 'static/images/lane1_current.jpg',
        'reference': 'static/images/lane1_empty.jpg'
    },
    {
        'current': 'static/images/lane2_current.jpg',
        'reference': 'static/images/lane2_empty.jpg'
    },
    {
        'current': 'static/images/lane3_current.jpg',
        'reference': 'static/images/lane3_empty.jpg'
    },
    {
        'current': 'static/images/lane4_current.jpg',
        'reference': 'static/images/lane4_empty.jpg'
    }
]

junction = TrafficJunction(lanes)

simulation_process = None

def run_traffic_system():
    while current_state['is_running']:
        for i in range(len(lanes)):
            current_state['active_lane'] = i + 1
            timing, density = junction.process_lane(i)
            current_state['density'] = round(density, 2)
            
            # Green light phase
            current_state['light_status'] = 'GREEN'
            for remaining in range(timing, 0, -1):
                current_state['timer'] = remaining
                time.sleep(1)
                if not current_state['is_running']:
                    return
            
            # Yellow light phase
            current_state['light_status'] = 'YELLOW'
            for remaining in range(3, 0, -1):
                current_state['timer'] = remaining
                time.sleep(1)
                if not current_state['is_running']:
                    return
            
            current_state['light_status'] = 'RED'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start')
def start_system():
    if not current_state['is_running']:
        current_state['is_running'] = True
        thread = threading.Thread(target=run_traffic_system)
        thread.start()
    return jsonify({'status': 'success'})

@app.route('/stop')
def stop_system():
    current_state['is_running'] = False
    return jsonify({'status': 'success'})

@app.route('/status')
def get_status():
    return jsonify(current_state)

@app.route('/simulation')
def launch_simulation():
    global simulation_process
    
    # If there's an existing simulation, terminate it
    if simulation_process and simulation_process.is_alive():
        simulation_process.terminate()
        simulation_process.join()
    
    # Start new simulation
    simulation_process = start_simulation()
    return jsonify({'status': 'simulation_started'})

@app.route('/stop_simulation')
def stop_simulation():
    global simulation_process
    if simulation_process and simulation_process.is_alive():
        simulation_process.terminate()
        simulation_process.join()
    return jsonify({'status': 'simulation_stopped'})

if __name__ == '__main__':
    multiprocessing.freeze_support()  # Required for Windows
    app.run(debug=True) 