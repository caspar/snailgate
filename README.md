Snailgate
=========

# UI Stuff

- libigl
- matplotlib
- html canvas

# Physics

## Input

- Collection of vertices `V = (#V, 2) double matrix`
- Collection of edges `E = (#E, 2) int matrix`
- Tags for vertices `VP = (#V, 1) int vector`(0 = not fixed, 1 = fixed)
- Tags for edges `EP = (#E, 1) int vector` (0 = spring, 1 = rods, 2 = ropes)
- Level of water `double z`

## Output

- Forces on the nodes `F = (#V, 2) double matrix`

## Future

- Explicit integration (forward Euler w/ Newton's law)
- Quasi-static solution (minimize potential energy of the system). Formulate energy wrt node positions
- Handling of rods: from 2 points coord (4 DOFs) -> 1 point + rotation (3 DOFs)

# Recommendations

Separate GUI part from the simulation part.

# Response from server

Set of frames with updated positions of vertices

# Development

## Setup

Install [node.js](https://nodejs.org/en/download/) for the javascript build system (webpack).

Install dependencies:

    pip install -r requirements.txt

    cd ui/client && npm i && cd ../..

Install linting tools globally, so that they work in the development environment:

    npm install -g eslint@2.12.0 eslint-plugin-react@5.1.1

## Running the application

Start the server:

    ./start.sh

Open the url `http://localhost:5000` in the browser.

## Running tests/linting tools

To run the linting tools:

    ./lint.sh

# Deployment

Build the javascript:

    ./build_client.sh

Start the server in production mode:

    ./start_server_prod.sh
