import React from 'react'
import { find } from 'lodash'
import { toSvgX, toSvgY } from '../utils/svg'

const waterColor ='#4BAFC8'

const getOriginVertex = (vertices) => {
    const verticesAtBottom = []
    const numV = vertices.length

    var i
    for (i=0; i<numV; i++) {
        var vertex = vertices[i]

        if (vertex[1] < 1e-5) {
            verticesAtBottom.push(i)
        }
    }
    
    var origin = 0
    var maxX = -Infinity
    for (i=0; i<verticesAtBottom.length; i++) {
        var index = verticesAtBottom[i]
        if (vertices[index][0] > maxX) {
            maxX = vertices[index][0]
            origin = index
        }
    }
    return origin
}

const equalEdges = (edge1, edge2) => {
    if (edge1[0] == edge2[0] && edge1[1] == edge2[1]) {
        return true
    }
    if (edge1[1] == edge2[0] && edge1[0] == edge2[1]) {
        return true
    }
    return false
}

// Method that preorders edges in such a way that they follow a natural order of vertices and edges from the initial floor vertex
const preOrderEdges = (vertices, edges, origin) => {
    let new_edges = [];
    const numE = edges.length;
    // starts at the origin
    let current_v = origin;

    // continues searching for next edge to touch water until we achieve a point higher than hw
    while (true) {
        let last_edge = [-1, -1];
        if (new_edges.length > 0)
            last_edge = new_edges[new_edges.length - 1].v;

        // find all edges connecting to the current vertex
        let connected_edge = [-1, -1];
        let connected_edge_index = -1;

        for (let k = 0; k < numE; k++) {
            let edge_vertices = edges[k].v;
            let edge_type = edges[k].type;
            if (equalEdges(edge_vertices, last_edge) || edge_type == 2) {
                continue;
            }

            if (edge_vertices[0] == current_v) {
                connected_edge = edge_vertices;
                connected_edge_index = k;
                break;
            }

            // flip if necessary
            if (edge_vertices[1] == current_v) {
                connected_edge = [edge_vertices[1], edge_vertices[0]];
                connected_edge_index = k;
                break;
            }
        }

        if (connected_edge_index == -1)
            break;

        // Add new edge
        let new_edge_to_be_added = {
            v: connected_edge,
            type: edges[connected_edge_index].type,
            length: edges[connected_edge_index].length
        };

        new_edges.push(new_edge_to_be_added);

        // update current vertex
        current_v = connected_edge[1]
    }


    for (let k = 0; k < numE; k++) {
        let edge_type = edges[k].type;
        if (edge_type == 2) {
            let new_edge_to_be_added = {
                v: edges[k].v,
                type: edges[k].type,
                length: edges[k].length
            };

            new_edges.push(new_edge_to_be_added);
        }

    }

    return new_edges
}

const computeWaterPolygon = (vertices, VBR, edges, origin, waterLevel) => {
    let modifiedVertex;
    let result = [];
    let polygon = [];

    let exit_position = -10000;
    let in_water = true;

    const numE = edges.length;
    const numV = vertices.length;

    let buoy_edge = -1;

    // add origin
    result.push(vertices[origin]);

    // continues searching for next edge to touch water until we achieve a point higher than hw
    for (let k = 0; k < numE; k++) {
        let current_edge = edges[k];

        if (current_edge.type == 2)
            continue;

        const last_v = current_edge.v[0];
        const current_v = current_edge.v[1];

        if (in_water) {
            // if some of the vertices is under water, the edge is wet
            if (vertices[last_v][1] < waterLevel || vertices[current_v][1] < waterLevel) {
                if (vertices[current_v][1] >= waterLevel) {
                    const v0 = vertices[last_v];
                    const v1 = vertices[current_v];

                    const angular_coeff = (v1[1] - v0[1]) / (v1[0] - v0[0]);
                    const newX = (waterLevel - v0[1]) / angular_coeff + v0[0];
                    modifiedVertex = [newX, waterLevel];
                    polygon.push(modifiedVertex)
                }
                else {
                    polygon.push(vertices[current_edge.v[1]]);
                }
            }
            // if the edge is leaving water, time to save our wet edges
            if (vertices[last_v][1] < waterLevel && waterLevel <= (vertices[current_v][1] + VBR[current_v])) {
                // set flat correctly, since we are leaving water
                in_water = false;

                let x1 = vertices[last_v][0];
                let y1 = vertices[last_v][1];
                let x2 = vertices[current_v][0];
                let y2 = vertices[current_v][1];

                let new_exit_position = x2 - (y2 - waterLevel) * (x2 - x1) / (y2 - y1);

                if (waterLevel > y2) {
                    new_exit_position = x2;

                    if (new_exit_position >= exit_position)
                        // if buoy is holding water (and it is the last buoy), add additional vertex showing this
                        buoy_edge = [x2, waterLevel];
                }

                if (new_exit_position >= exit_position)
                    result = result.concat(polygon);

                polygon = [];

                exit_position = new_exit_position
            }
        }
        else {
            // Entering water level?
            if (waterLevel > vertices[current_v][1]) {
                let x1 = vertices[last_v][0];
                let y1 = vertices[last_v][1];
                let x2 = vertices[current_v][0];
                let y2 = vertices[current_v][1];

                let enter_position = x2 - (y2 - waterLevel) * (x2 - x1) / (y2 - y1);

                if (waterLevel > y1)
                    enter_position = x1;

                // if it is entering to the right of the exit position, it is fine
                if (enter_position >= exit_position) {
                    // if buoy is holding water (and it is the last buoy), add additional vertex showing this
                    if (y2 + VBR[current_v] > waterLevel) {
                        buoy_edge = [x2, waterLevel];
                    }

                    const v0 = vertices[last_v];
                    const v1 = vertices[current_v];

                    const angular_coeff = (v1[1] - v0[1]) / (v1[0] - v0[0]);
                    const newX = (waterLevel - v0[1]) / angular_coeff + v0[0];
                    modifiedVertex = [newX, waterLevel];
                    polygon.push(modifiedVertex);
                    polygon.push(v1);

                    // set flat correctly, since we are leaving water
                    in_water = true
                }
            }

        }
    }

    // if empty, everything is under water! =O
    if (result.length === 1) {
        return [[100, 0.0], [-100, 0], [-100, waterLevel], [100, waterLevel]]
    }

    // add extra vertices to close polygon
    if (buoy_edge !== -1)
        result.push(buoy_edge);
    result.push([100, waterLevel]);
    result.push([100, 0.0]);

    return result
}


const oldcomputeWaterPolygon = (vertices, edges, origin, waterLevel) => {
    const polygon = []

    var currentV = origin
    var stillInWater = true

    // continues searching for next edge to touch water until we achieve a point
    // higher than hw
    polygon.push(vertices[currentV])
    var lastEdge = [-1, -1]
    while (stillInWater) {
        // find all edges connecting to the current vertex
        var connectedEdges = []
        const numE = edges.length
        var i = 0
        for (i = 0; i < numE; i++) {
            // verify if it is the same edge
            var edgeVertices = edges[i].v
            var edgeType = edges[i].type
            if (equalEdges(edgeVertices, lastEdge) || edgeType == 2) {
                continue
            }

            if (edgeVertices[0] == currentV) {
                connectedEdges.push(edgeVertices)
            }

            // flip if necessary
            if (edgeVertices[1] == currentV) {
                connectedEdges.push([edgeVertices[1], edgeVertices[0]])
            }
        }

        if (connectedEdges.length > 1) {
            console.error("More than one edge (non rope) connected to same vertex")
            stillInWater = false
        }
        else if(connectedEdges.length == 1) {
            const previousV = currentV
            currentV = connectedEdges[0][1]

            if (vertices[currentV][1] >= waterLevel) {
                const v0 = [vertices[previousV][0], vertices[previousV][1]]
                const v1 = [vertices[currentV][0], vertices[currentV][1]]

                const angularCoeff = (v1[1] - v0[1])/(v1[0] - v0[0])
                const newX = (waterLevel - v0[1])/angularCoeff + v0[0]
                var modifiedVertex = [newX, waterLevel]
                polygon.push(modifiedVertex)
                stillInWater = false
            }
            else {
                lastEdge = connectedEdges[0]
                var newVertex = [vertices[currentV][0], vertices[currentV][1]]
                polygon.push(newVertex)
            }
        }
        else {
            // it means it ended with the whole structure in the water. Then, add a new vertex to the polygon
            var lastVertex = polygon[polygon.length-1]
            polygon.push([lastVertex[0], waterLevel])
            stillInWater = false
        }
    }

    // add extra vertices to close polygon
    polygon.push([100, waterLevel])
    polygon.push([100, 0.0])

    return polygon
}

const toSvgPolygon = (polygon) => {
    const numV = polygon.length
    var i = 0
    var svgPolygon = ''

    for (i=0; i<numV; i++){
        svgPolygon += toSvgX(polygon[i][0]) + ',' + toSvgY(polygon[i][1]) + ' '
    }

    return svgPolygon
}

function roundNumber(num, dec) {
    return Math.round(num * Math.pow(10, dec)) / Math.pow(10, dec);
}

const Water = ({ vertices, level, edges, simulatedVertexPositions }) => {
    const firstVertexAboveGround = find(vertices, vertex => vertex.p[1] > 0)
    if (!firstVertexAboveGround) return <g />

    var currentVBR = []
    for (i = 0; i < vertices.length; i++) {
        if (typeof vertices[i].boyantRadius == 'undefined')
            currentVBR.push(0.0);
        else
            currentVBR.push(vertices[i].boyantRadius);
    }

    var currentVertices = []
    if (typeof simulatedVertexPositions == 'undefined') {
        var i = 0
        for (i = 0; i < vertices.length; i++) {
            currentVertices.push(vertices[i].p)
        }
    } else {
        currentVertices = simulatedVertexPositions
    }

    const origin = getOriginVertex(currentVertices)
    let ordered_edges = preOrderEdges(currentVertices, edges, origin)
    const waterPolygon = computeWaterPolygon(currentVertices, currentVBR, ordered_edges, origin, level);
    const svgPolygon = toSvgPolygon(waterPolygon)

    var xTextPos = toSvgX(currentVertices[origin][0] + 0.1);
    var yTextPos = toSvgY(level)

    // pass to string with correct number of digits
    var levelString = roundNumber(level, 4).toString();
    if (levelString.indexOf('.') == -1) levelString += '.';
    while (levelString.length < levelString.indexOf('.') + 5) levelString += '0';

    return <g>
        <polygon points={svgPolygon} fill={waterColor} />
        <text x={xTextPos} y={yTextPos} fill="blue">Water level: {levelString}m</text>
      </g>
}

export default Water
