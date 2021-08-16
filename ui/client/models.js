import { getLength, getNormalizedSlope } from './utils/geometry'

import { map, clone, each, some, range, reduce, includes, filter, isNumber, random, orderBy } from 'lodash'

export const vertexTypes = {
  notFixed: 0,
  fixed: 1
}

export const edgeTypes = {
  spring: 0,
  rod: 0,
  rope: 2
}

export const forceTypes = {
  total: 'total',
  waterPressure: 'waterPressure',
  tensor: 'tensor',
  gravity: 'gravity',
  boyancy: 'boyancy'
}

export const forceColors = {
  [forceTypes.total]: 'red',
  [forceTypes.waterPressure]: 'blue',
  [forceTypes.tensor]: 'green',
  [forceTypes.gravity]: 'black',
  [forceTypes.boyancy]: 'black'
}

export const toSimulationData = (vertices, edges, waterLevel) => ({
  vertices: map(vertices, ({ p }) => p),
  edges: map(edges, ({ v }) => v),
  vertexTypes: map(vertices, ({ type }) => type),
  vertexBoyantRadiai: map(vertices, ({ boyantRadius = 0 }) => boyantRadius),
  edgeTypes: map(edges, ({ type }) => type),
  edgeLengths: map(edges, ({ length }) => length),
  edgeSplits: map(edges, ({ splitSize }) => splitSize),
  waterLevel
})

export const fromSimulationData = ({ vertices, edges, vertexTypes, vertexBoyantRadiai = [], edgeTypes, waterLevel, edgeLengths = [], edgeSplits = [] }) => ({
  edges: map(edges, (v, i) => ({
    v,
    type: edgeTypes[i],
    length: edgeLengths[i] || getLength(vertices[v[0]], vertices[v[1]]),
    splitSize: edgeSplits[i] || 1
  })),
  vertices: map(vertices, (p, i) => ({ p, type: vertexTypes[i], boyantRadius: vertexBoyantRadiai[i] })),
  waterLevel
})

export const toSimulationResultsData = simulationResults => simulationResults

export const parseForcesFromServer = forcesByStep => (
  map(forcesByStep, forceStep => (
    map(forceStep, force => ({
      [forceTypes.total]: [force[0], force[1]],
      [forceTypes.waterPressure]: [force[2], force[3]],
      [forceTypes.tensor]: [force[4], force[5]],
      [forceTypes.gravity]: [force[6], force[7]],
      [forceTypes.boyancy]: [force[8], force[9]]
    }))
  ))
)

export const splitEdge = (edges, vertices, vertexIdToSplitOn, edgeIdToSplit) => {
  const splitEdges = clone(edges)

  const originalSecondVertex = splitEdges[edgeIdToSplit].v[1]
  splitEdges[edgeIdToSplit].v[1] = vertexIdToSplitOn

  splitEdges.push({
    v: [vertexIdToSplitOn, originalSecondVertex],
    type: splitEdges[edgeIdToSplit].type
  })

  return splitEdges
}

const recalculateEdgeLength = (edge, vertices) => (
  edge.type === edgeTypes.rope && isNumber(edge.length) ? edge.length : getLength(vertices[edge.v[0]].p, vertices[edge.v[1]].p)
)

export const updateEdgeLengths = (edges, vertices) => (
  map(edges, edge => ({
    ...edge,
    length: recalculateEdgeLength(edge, vertices)
  }))
)

const noEdgeExistsWithVertex = (edges, vertexId) => (
  !some(edges, edge => (
    some(edge.v, vertex => vertex === vertexId)
  ))
)

export const deleteEdge = (originalEdges, originalvertices, edgeIdToDelete) => {
  const edges = clone(originalEdges)
  const vertices = clone(originalvertices)

  // delete edge
  const edge = edges.splice(edgeIdToDelete, 1)[0]

  each([0, 1], i => {
    const vertex = edge.v[i]

    // never delete the first vertex
    if (vertex !== 0) {
      if (noEdgeExistsWithVertex(edges, vertex)) {
        // remove the vertex
        vertices.splice(vertex, 1)
        // for each edge, move vertices back to account for removed vertex
        each(edges, edge => {
          if (edge.v[0] > vertex)
            edge.v[0]--
          if (edge.v[1] > vertex)
            edge.v[1]--
        })
        // shift second vertex back
        if (i === 0 && vertex > edge.v[1])
          edge.v[1]--
      }
    }
  })

  return { edges, vertices }
}

const getEvenlySplitNewVertexPositions = (p1, p2, splitSize) => {
  const edgeLength = getLength(p1, p2)
  const splitEdgeLength = edgeLength / splitSize

  const slope = getNormalizedSlope(p1, p2)

  let lastPoint = p1

  return reduce(range(1, splitSize), result => {
    const newPoint = [lastPoint[0] + splitEdgeLength * slope[0], lastPoint[1] + splitEdgeLength * slope[1]]

    result.push({
      p: newPoint,
      type: vertexTypes.notFixed
    })

    lastPoint = newPoint

    return result
  }, [])
}

const getRandomSplitNewVertexPositions = (p1, p2, splitSize) => {
  const edgeLength = getLength(p1, p2)
  const slope = getNormalizedSlope(p1, p2)

  const newvertices = reduce(range(1, splitSize), result => {
    const change = random(0, edgeLength, true)
    const newPoint = [p1[0] + change * slope[0], p1[1] + change * slope[1]]

    result.push({
      p: newPoint,
      type: vertexTypes.notFixed
    })

    return result
  }, [])

  const sortOrder = p1[0] < p2[0] ? 1 : -1

  // make sure to sort the vertices if they were randomized
  return orderBy(newvertices, ({ p }) => sortOrder * p[0])
}

export const splitEdgeBySize = (originalEdges, originalvertices, edgeId, splitSize, randomSplitVertexPositions) => {
  const edge = originalEdges[edgeId]

  const [v1, v2] = [originalvertices[edge.v[0]], originalvertices[edge.v[1]]]

  let newvertices
  if (randomSplitVertexPositions)
    newvertices = getRandomSplitNewVertexPositions(v1.p, v2.p, splitSize)
  else
    newvertices = getEvenlySplitNewVertexPositions(v1.p, v2.p, splitSize)

  const currentLastVertexIndex = originalvertices.length - 1

  const vertices = [
    ...originalvertices,
    ...newvertices
  ]

  const newEdges = reduce(range(0, splitSize), (result, edgeIndex) => {
    const v1 = edgeIndex === 0 ? edge.v[0] : currentLastVertexIndex + edgeIndex
    const v2 = edgeIndex === splitSize - 1 ? edge.v[1] : currentLastVertexIndex + edgeIndex + 1

    const newEdge = {
      type: edge.type,
      length: getLength(vertices[v1].p, vertices[v2].p),
      v: [v1, v2]
    }

    result.push(newEdge)

    return result
  }, [])

  const edges = [
    ...originalEdges,
    ...newEdges
  ]

  return { edges, vertices }
}

export const splitEdgesWithSplitSize = (originalEdges, originalvertices, randomSplitVertexPositions) => {
  const edgesToSplit = reduce(originalEdges, (result, { splitSize }, edgeIndex) => {
    if (splitSize > 1)
      result.push({
        edgeIndex,
        splitSize
      })

    return result
  }, [])

  let { edges, vertices } = reduce(edgesToSplit, ({ edges: originalEdges, vertices: originalvertices }, { splitSize, edgeIndex }) => {
    return splitEdgeBySize(originalEdges, originalvertices, edgeIndex, splitSize, randomSplitVertexPositions)
  }, { edges: originalEdges, vertices: originalvertices })

  // delete all split edges
  edges = filter(edges, ({ splitSize = 1}) => splitSize <= 1)

  return { edges, vertices }
}

export const toggleShowForce = (showForces, showForceType) => {
  let result

  if (includes(showForces, showForceType))
    result = filter(showForces, showForce => showForce !== showForceType)
  else
    result = [...showForces, showForceType]

  return result
}
