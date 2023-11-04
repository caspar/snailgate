import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'simulation'))

import json

import simulatorLib
from flask import Flask, jsonify, render_template, request
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

scenariosDirectory = os.path.join(os.path.dirname(__file__), '..', '..', 'scenarios')

@app.route('/')
def home():
    scenarios = os.listdir(scenariosDirectory)
    scenario = request.args.get('scenario')
    scenarioJson = {}

    if scenario is not None:
        filePath = os.path.join(scenariosDirectory, scenario)
        print('loading json at', filePath)
        with open(filePath) as dataFile:
            scenarioJson = json.load(dataFile)
        print('loaded it')

    static_js = os.environ['STATIC_JS'] == 'true' if 'STATIC_JS' in os.environ else False

    return render_template('index.html', scenarios=scenarios, scenario=scenario, scenarioJson=scenarioJson, static_js=static_js)

def emitBatch(U, F, wl, totalSteps):
    jsonResult = {
        'vertexPositions': U.tolist(),
        'forces': F.tolist(),
        'waterLevel': wl.tolist(),
        'totalSteps': totalSteps
    }

    # socketio.emit('results', jsonResult, broadcast=True)
    socketio.emit('results', jsonResult)


simulatorCanceled = False

@app.route('/simulate', methods=['POST'])
def simulate():
    print('parsing json')
    postBody = request.get_json(force=True, silent=True, cache=False)

    print(postBody)

    V, E, VP, EP, EL, hw, VBR, water_speed, timeStep, maxIterations, simulationMethod = simulatorLib.from_json(postBody)

    method = None
    batchDuration = None

    if (simulationMethod == "Forward Euler"):
        method = simulatorLib.simulate
        batchDuration = 0.5
    elif (simulationMethod == "Backward Euler"):
        method = simulatorLib.implicit_simulation
        batchDuration = 1
    else:
        return jsonify(success=false)

    print('Running simulation!')
    global simulatorCanceled
    for U, F, wl, totalSteps in method(V, E, VP, EP, EL, VBR, hw, water_speed, timeStep, maxIterations, batchDuration):
        emitBatch(U, F, wl, totalSteps)
        socketio.sleep(1.0/10000.0)
        if simulatorCanceled:
            simulatorCanceled=False
            break

    return jsonify(
        success=True,
    )

@socketio.on('cancel')
def cancelSimulation():
    global simulatorCanceled
    simulatorCanceled=True


if __name__ == '__main__':
    socketio.run(app)
