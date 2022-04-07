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

export const toSimulationData = (verteces, edges, waterLevel) => ({
  verteces: map(verteces, ({ p }) => p),
  edges: map(edges, ({ v }) => v),
  vertexTypes: map(verteces, ({ type }) => type),
  vertexBoyantRadiai: map(verteces, ({ boyantRadius = 0 }) => boyantRadius),
  edgeTypes: map(edges, ({ type }) => type),
  edgeLengths: map(edges, ({ length }) => length),
  edgeSplits: map(edges, ({ splitSize }) => splitSize),
  waterLevel
})

export const fromSimulationData = ({ verteces, edges, vertexTypes, vertexBoyantRadiai = [], edgeTypes, waterLevel, edgeLengths = [], edgeSplits = [] }) => ({
  edges: map(edges, (v, i) => ({
    v,
    type: edgeTypes[i],
    length: edgeLengths[i] || getLength(verteces[v[0]], verteces[v[1]]),
    splitSize: edgeSplits[i] || 1
  })),
  verteces: map(verteces, (p, i) => ({ p, type: vertexTypes[i], boyantRadius: vertexBoyantRadiai[i] })),
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

export const splitEdge = (edges, verteces, vertexIdToSplitOn, edgeIdToSplit) => {
  const splitEdges = clone(edges)

  const originalSecondVertex = splitEdges[edgeIdToSplit].v[1]
  splitEdges[edgeIdToSplit].v[1] = vertexIdToSplitOn

  splitEdges.push({
    v: [vertexIdToSplitOn, originalSecondVertex],
    type: splitEdges[edgeIdToSplit].type
  })

  return splitEdges
}

const recalculateEdgeLength = (edge, verteces) => (
  edge.type === edgeTypes.rope && isNumber(edge.length) ? edge.length : getLength(verteces[edge.v[0]].p, verteces[edge.v[1]].p)
)

export const updateEdgeLengths = (edges, verteces) => (
  map(edges, edge => ({
    ...edge,
    length: recalculateEdgeLength(edge, verteces)
  }))
)

const noEdgeExistsWithVertex = (edges, vertexId) => (
  !some(edges, edge => (
    some(edge.v, vertex => vertex === vertexId)
  ))
)

export const deleteEdge = (originalEdges, originalVerteces, edgeIdToDelete) => {
  const edges = clone(originalEdges)
  const verteces = clone(originalVerteces)

  // delete edge
  const edge = edges.splice(edgeIdToDelete, 1)[0]

  each([0, 1], i => {
    const vertex = edge.v[i]

    // never delete the first vertex
    if (vertex !== 0) {
      if (noEdgeExistsWithVertex(edges, vertex)) {
        // remove the vertex
        verteces.splice(vertex, 1)
        // for each edge, move verteces back to account for removed vertex
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

  return { edges, verteces }
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

  const newVerteces = reduce(range(1, splitSize), result => {
    const change = random(0, edgeLength, true)
    const newPoint = [p1[0] + change * slope[0], p1[1] + change * slope[1]]

    result.push({
      p: newPoint,
      type: vertexTypes.notFixed
    })

    return result
  }, [])

  const sortOrder = p1[0] < p2[0] ? 1 : -1

  // make sure to sort the verteces if they were randomized
  return orderBy(newVerteces, ({ p }) => sortOrder * p[0])
}

export const splitEdgeBySize = (originalEdges, originalVerteces, edgeId, splitSize, randomSplitVertexPositions) => {
  const edge = originalEdges[edgeId]

  const [v1, v2] = [originalVerteces[edge.v[0]], originalVerteces[edge.v[1]]]

  let newVerteces
  if (randomSplitVertexPositions)
    newVerteces = getRandomSplitNewVertexPositions(v1.p, v2.p, splitSize)
  else
    newVerteces = getEvenlySplitNewVertexPositions(v1.p, v2.p, splitSize)

  const currentLastVertexIndex = originalVerteces.length - 1

  const verteces = [
    ...originalVerteces,
    ...newVerteces
  ]

  const newEdges = reduce(range(0, splitSize), (result, edgeIndex) => {
    const v1 = edgeIndex === 0 ? edge.v[0] : currentLastVertexIndex + edgeIndex
    const v2 = edgeIndex === splitSize - 1 ? edge.v[1] : currentLastVertexIndex + edgeIndex + 1

    const newEdge = {
      type: edge.type,
      length: getLength(verteces[v1].p, verteces[v2].p),
      v: [v1, v2]
    }

    result.push(newEdge)

    return result
  }, [])

  const edges = [
    ...originalEdges,
    ...newEdges
  ]

  return { edges, verteces }
}

export const splitEdgesWithSplitSize = (originalEdges, originalVerteces, randomSplitVertexPositions) => {
  const edgesToSplit = reduce(originalEdges, (result, { splitSize }, edgeIndex) => {
    if (splitSize > 1)
      result.push({
        edgeIndex,
        splitSize
      })

    return result
  }, [])

  let { edges, verteces } = reduce(edgesToSplit, ({ edges: originalEdges, verteces: originalVerteces }, { splitSize, edgeIndex }) => {
    return splitEdgeBySize(originalEdges, originalVerteces, edgeIndex, splitSize, randomSplitVertexPositions)
  }, { edges: originalEdges, verteces: originalVerteces })

  // delete all split edges
  edges = filter(edges, ({ splitSize = 1}) => splitSize <= 1)

  return { edges, verteces }
}

export const toggleShowForce = (showForces, showForceType) => {
  let result

  if (includes(showForces, showForceType))
    result = filter(showForces, showForce => showForce !== showForceType)
  else
    result = [...showForces, showForceType]

  return result
}
