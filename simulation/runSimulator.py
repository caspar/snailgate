#!/usr/bin/env python
import json
import sys

import plotLib
import simulatorLib

if len(sys.argv) != 2:
    print("usage: ./simulator.py scenarioNumber")
    print("example: ./simulator.py 1")
    sys.exit(-1)

# Main

if sys.argv[1].isdigit():
    if sys.argv[1] == '1':
        V, E, VP, EP, EL, VBR, hw = simulatorLib.setup_original_watergate_example()
    elif sys.argv[1] == '2':
        V, E, VP, EP, EL, VBR, hw = simulatorLib.setup_original_watergate_example2()
    elif sys.argv[1] == '3':
        V, E, VP, EP, EL, VBR, hw = simulatorLib.setup_original_watergate_example3()
    elif sys.argv[1] == '4':
        V, E, VP, EP, EL, VBR, hw = simulatorLib.setup_original_watergate_example4()
    elif sys.argv[1] == '5':
        V, E, VP, EP, EL, VBR, hw = simulatorLib.setup_original_watergate_example5()
    elif sys.argv[1] == '6':
        V, E, VP, EP, EL, VBR, hw = simulatorLib.setup_original_watergate_example6()
    elif sys.argv[1] == '7':
        V, E, VP, EP, EL, VBR, hw = simulatorLib.setup_original_watergate_example7()

    else:
        print("No scenario with this number")
        sys.exit(-1)
else:
    data_file = open(sys.argv[1])
    data = json.load(data_file)
    V, E, VP, EP, EL, hw, VBR, water_speed, time_step, max_iterations, simulation_method = simulatorLib.from_json(data)

water_speed = 0.2
# noinspection PyRedeclaration
time_step = 0.0001

# run the simulator, obtaining positions, velocities and forces over time
for U, F, wl, totalSteps in simulatorLib.implicit_simulation(V, E, VP, EP, EL, VBR, hw, water_speed, time_step, 5000, 8000):
    # draw simulation
    #plotLib.draw_simulation(U, F[:, :, 0:2], E, EP, hw, water_speed, time_step, 2)
    print("Finish")
