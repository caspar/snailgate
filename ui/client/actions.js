import { edgeTypes, vertexTypes, toSimulationData, fromSimulationData, splitEdge, deleteEdge, parseForcesFromServer, updateEdgeLengths, splitEdgesWithSplitSize, toSimulationResultsData } from 'models'
import { findClosetsPointOnEdge } from './utils/geometry'
import { isNumber, clone, clamp, floor } from 'lodash'
import { saveAs } from 'file-saver'
import socketClient from './socketClient'
import {
  isAddingEdge,
  onFirstVertex,
  onSecondVertex,
  selectedVertexId,
  selectedEdgeId,
  availableSimulationSteps,
  simulationStep
} from './selectors'

import { post } from 'axios'

export const actionTypes = {
  UPDATE_WATER_LEVEL: 'UPDATE_WATER_LEVEL',
  START_RUNNING_SIMULATION: 'START_RUNNING_SIMULATION',
  FINISHED_RUNNING_SIMULATION: 'FINISHED_RUNNING_SIMULATION',
  EDGE_CLICKED: 'EDGE_CLICKED',
  VERTEX_CLICKED: 'VERTEX_CLICKED',
  EDGE_HOVERED: 'EDGE_HOVERED',
  VERTEX_HOVERED: 'VERTEX_HOVERED',
  FLOOR_CLICKED: 'FLOOR_CLICKED',
  EMPTY_SPACE_CLICKED: 'EMPTY_SPACE_CLICKED',
  CANCELING_SIMULATION: 'CANCELING_SIMULATION',
  ADD_MODE_ENTERED: 'ADD_MODE_ENTERED',
  FIRST_VERTEX_SET: 'FIRST_VERTEX_SET',
  EDGE_SELECTED: 'EDGE_SELECTED',
  VERTEX_SELECTED: 'VERTEX_SELECTED',
  EDGE_ADDED: 'EDGE_ADDED',
  SIMULATION_RESULTS_RECEIVED: 'SIMULATION_RESULTS_RECEIVED',
  DATA_IMPORTED: 'DATA_IMPORTED',
  EDGES_UPDATED: 'EDGES_UPDATED',
  vertices_UPDATED: 'vertices_UPDATED',
  CANCELED: 'CANCELED',
  EDGE_DELETED: 'EDGE_DELETED',
  SIMULATION_STEP_CHANGED: 'SIMULATION_STEP_CHANGED',
  SIMULATION_ENDED: 'SIMULATION_ENDED',
  SHOW_FORCE_TOGGLED: 'SHOW_FORCE_TOGGLED',
  SIMULATION_LOADED: 'SIMULATION_LOADED',
  SCENARIO_LOADED: 'SCENARIO_LOADED',
  STARTED_MOVING_VERTEX: 'STARTED_MOVING_VERTEX'
}

export const scenarioLoaded = scenario => ({
  type: actionTypes.SCENARIO_LOADED,
  ...scenario
})

export const updateWaterLevel = waterLevel => ({
  type: actionTypes.UPDATE_WATER_LEVEL,
  waterLevel
})

// editor controls

export const enterAddMode = (edgeType, firstVertexType) => ({
  type: actionTypes.ADD_MODE_ENTERED,
  edgeType,
  firstVertexType
})

const finishAddingEdge = (existingVertexId, newVertex, secondVertexEdgeId) => (dispatch, getState) => {
  const state = getState()
  const vertices = clone(state.vertices)
  const addMode = state.addMode
  let edges = clone(state.edges)

  const vertexIds = [null, null]

  if (isNumber(addMode.firstVertexId))
    vertexIds[0] = addMode.firstVertexId
  else {
    vertices.push({
      p: addMode.firstVertex,
      type: addMode.firstVertexType
    })
    vertexIds[0] = vertices.length - 1
  }

  if (isNumber(existingVertexId))
    vertexIds[1] = existingVertexId
  else {
    vertices.push(newVertex)
    vertexIds[1] = vertices.length - 1
  }

  if (isNumber(addMode.firstVertexEdgeId))
    edges = splitEdge(edges, vertices, vertexIds[0], addMode.firstVertexEdgeId)

  if (isNumber(secondVertexEdgeId))
    edges = splitEdge(edges, vertices, vertexIds[1], secondVertexEdgeId)

  edges.push({
    v: vertexIds,
    type: addMode.addingEdgeType
  })

  edges = updateEdgeLengths(edges, vertices)

  dispatch({
    type: actionTypes.EDGE_ADDED,
    vertices,
    edges
  })
}

export const firstVertexSet = (firstVertex, firstVertexType, firstVertexEdgeId) => ({
  type: actionTypes.FIRST_VERTEX_SET,
  firstVertex,
  firstVertexType,
  firstVertexEdgeId
})


export const edgeClicked = (edgeId, mouse) => (dispatch, getState) => {
  const state = getState()

  const vertexIds = state.edges[edgeId].v
  const pointOnEdge = findClosetsPointOnEdge(
    state.vertices[vertexIds[0]].p,
    state.vertices[vertexIds[1]].p,
    mouse
  )

  // if point is on floor, its a fixed vertex type
  const vertexType = pointOnEdge[1] === 0 ? vertexTypes.fixed : vertexTypes.notFixed

  if (isAddingEdge(state)) {
    // dont allow clicking on ropes
    if (state.edges[edgeId].type === edgeTypes.rope) return

    if (onFirstVertex(state)) {
      dispatch({
        type: actionTypes.FIRST_VERTEX_SET,
        firstVertex: pointOnEdge,
        firstVertexEdgeId: edgeId,
        firstVertexType: vertexType
      })
    } else {
      dispatch(finishAddingEdge(null, { p: pointOnEdge, type: vertexType }, edgeId))
    }
  } else {
    dispatch({
      type: actionTypes.EDGE_SELECTED,
      edgeId
    })
  }
}

export const vertexClicked = vertexId => (dispatch, getState) => {
  const state = getState()
  if (isAddingEdge(state)) {
    const vertex = state.vertices[vertexId]

    if (onFirstVertex(state)) {
      dispatch({
        type: actionTypes.FIRST_VERTEX_SET,
        firstVertex: vertex.p,
        firstVertexId: vertexId
      })
    } else {
      dispatch(finishAddingEdge(vertexId))
    }
  } else {
    dispatch({
      type: actionTypes.VERTEX_SELECTED,
      vertexId
    })
  }
}

export const edgeHovered = (edgeId, mouseOver) => (dispatch, getState) => {
  const state = getState()

  if (!mouseOver)
    dispatch({
      type: actionTypes.EDGE_HOVERED
    })

  else {
    // don't allow connecting middle of rope to edges, so don't let it be hovered on
    if (isAddingEdge(state) && state.edges[edgeId].type === edgeTypes.rope)
      return

    dispatch({
      type: actionTypes.EDGE_HOVERED,
      edgeId
    })
  }
}

export const vertexHovered = (vertexId, mouseOver) => {
  if (!mouseOver)
    return {
      type: actionTypes.VERTEX_HOVERED
    }

  return {
    type: actionTypes.VERTEX_HOVERED,
    vertexId
  }
}

export const floorClicked = mouse => (dispatch, getState) => {
  const state = getState()
  // use x and y corresponding to top of floor
  const pointOnFloor = [mouse[0], 0]

  if (!isAddingEdge(state)) return

  if (onFirstVertex(state)) {
    dispatch({
      type: actionTypes.FIRST_VERTEX_SET,
      firstVertex: pointOnFloor
    })
  } else if (state.addMode.addingEdgeType === edgeTypes.spring) {
    dispatch(finishAddingEdge(null, {p: pointOnFloor, type: vertexTypes.fixed }))
  }
}

export const emptySpaceClicked = mouse => (dispatch, getState) => {
  const state = getState()

  if (isAddingEdge(state) && onSecondVertex(state) && state.addMode.addingEdgeType === edgeTypes.spring)
    dispatch(finishAddingEdge(null, {p: mouse, type: vertexTypes.notFixed }))
  else
    dispatch({ type: actionTypes.EDGE_SELECTED })
}

export const importData = dataFromServer => {
  const { edges, vertices, waterLevel } = fromSimulationData(dataFromServer)

  return {
    type: actionTypes.DATA_IMPORTED,
    edges,
    vertices,
    waterLevel
  }
}

export const changeVertexBoyancy = boyantRadius => (dispatch, getState) => {
  const vertexId = selectedVertexId(getState())

  dispatch(updateVertex(vertexId, { boyantRadius }))
}

export const changeVertexFixed = fixed => (dispatch, getState) => {
  const state = getState()
  const vertexId = selectedVertexId(state)

  const type = fixed ? vertexTypes.fixed : vertexTypes.notFixed

  dispatch(updateVertex(vertexId, { type }))
}

export const moveVertex = (vertexId, position) => (
  updateVertex(vertexId, {p: position})
)

const updateVertex = (vertexId, update) => (dispatch, getState) => {
  const state = getState()
  const vertices = clone(state.vertices)

  vertices[vertexId] = {
    ...vertices[vertexId],
    ...update
  }

  dispatch({
    type: actionTypes.vertices_UPDATED,
    vertices
  })
}

export const changeEdgeLength = length => (dispatch, getState) => {
  dispatch(updateEdge(selectedEdgeId(getState()), { length }))
}

export const splitSelectedEdge = splitSize => (dispatch, getState) => {
  dispatch(updateEdge(selectedEdgeId(getState()), { splitSize }))
}

const updateEdge = (edgeId, update) => (dispatch, getState) => {
  const state = getState()
  const edges = clone(state.edges)

  edges[edgeId] = {
    ...edges[edgeId],
    ...update
  }

  dispatch({
    type: actionTypes.EDGES_UPDATED,
    edges
  })
}

export const cancel = () => ({
  type: actionTypes.CANCELED
})

export const tryDeleteSelectedEdge = () => (dispatch, getState) => {
  const state = getState()
  if (isNumber(selectedEdgeId(state))) {
    const { edges, vertices } = deleteEdge(state.edges, state.vertices, selectedEdgeId(state))

    dispatch({
      type: actionTypes.EDGE_DELETED,
      edges,
      vertices
    })
  }
}


// Simulation Actions

export const simulationResultsReceived = ({ forces, vertexPositions, waterLevel, totalSteps }) => ({
  type: actionTypes.SIMULATION_RESULTS_RECEIVED,
  vertexPositions,
  forces: parseForcesFromServer(forces),
  waterLevel,
  totalSteps
})

const getDataForServer = (edges, vertices, simulationSettings, waterLevel) => {
  const simulationData = toSimulationData(
    vertices,
    edges,
    waterLevel
  )

  return {
    ...simulationData,
    ...simulationSettings
  }
}

const startRunningSimulation = (simulationResults, simulationSettings = {}) => ({
  type: actionTypes.START_RUNNING_SIMULATION,
  simulationResults,
  simulationSettings
})

export const runSimulation = (simulationSettings, randomSplitVertexPositions) => (dispatch, getState) => {
  const state = getState()

  const { edges, vertices } = splitEdgesWithSplitSize(state.edges, state.vertices, randomSplitVertexPositions)

  dispatch(startRunningSimulation({
    vertexPositions: [],
    forces: [],
    waterLevel: [],
    edges,
    vertices
  }, simulationSettings))

  post('/simulate', getDataForServer(edges, vertices, simulationSettings, state.waterLevel))
    .then(() => {
      dispatch({
        type: actionTypes.FINISHED_RUNNING_SIMULATION
      })
    })
    .catch(() => {
      dispatch({
        type: actionTypes.FINISHED_RUNNING_SIMULATION
      })
      alert('simulation failed')
    })
}

export const cancelSimulation = () => dispatch => {
  socketClient.emit('cancel')
  dispatch({ type: actionTypes.CANCELING_SIMULATION })
}

export const setSimulationStep = newStep => (dispatch, getState) => {
  const step = clamp(newStep, 0, availableSimulationSteps(getState()) - 1)

  dispatch({
    type: actionTypes.SIMULATION_STEP_CHANGED,
    simulationStep: step
  })
}

export const advanceSimulation = () => (dispatch, getState) => {
  const state = getState()
  const step = simulationStep(state)

  if (step < availableSimulationSteps(state))
    dispatch(setSimulationStep(step + 1))
}

export const rewindSimulation = () => (dispatch, getState) => {
  const step = simulationStep(getState())

  if (step !== 0)
    dispatch(setSimulationStep(step -1))
}

export const endSimulation = () => ({
  type: actionTypes.SIMULATION_ENDED
})

export const setSimulationPercentage = percentage => (dispatch, getState) => {
  const state = getState()

  const step = floor(percentage * state.simulationResults.totalSteps)
  dispatch(setSimulationStep(step))
}

export const toggleShowForceType = forceType => ({
  type: actionTypes.SHOW_FORCE_TOGGLED,
  forceType
})

export const loadSimulationResults = files => dispatch => {
  const reader = new FileReader()
  reader.onload = e => {
    const simulationResults = JSON.parse(e.target.result)
    dispatch(startRunningSimulation(simulationResults))
    dispatch({
      type: actionTypes.FINISHED_RUNNING_SIMULATION
    })
  }

  reader.readAsText(files[0])
}

export const saveSimulationResults = () => (dispatch, getState) => {
  const simulationResultsData = toSimulationResultsData(getState().simulationResults)

  const blob = new Blob([JSON.stringify(simulationResultsData)], {type: 'text/json;charset=utf-8'})
  saveAs(blob, 'simulation_results.json')
}
