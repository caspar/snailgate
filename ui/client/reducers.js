import { actionTypes } from './actions'
import { vertexTypes, forceTypes, toggleShowForce } from 'models'
import { combineReducers } from 'redux'

const initialverticesState = [
  {
    p: [1, 0],
    type: vertexTypes.fixed
  }
]

const vertices = (state = initialverticesState, action) => {
  switch(action.type) {
  case actionTypes.EDGE_ADDED:
  case actionTypes.DATA_IMPORTED:
  case actionTypes.vertices_UPDATED:
  case actionTypes.EDGE_DELETED:
  case actionTypes.SCENARIO_LOADED:
    return action.vertices
  default:
    return state
  }
}

const edges = (state = [], action) => {
  switch(action.type) {
  case actionTypes.EDGE_ADDED:
  case actionTypes.DATA_IMPORTED:
  case actionTypes.EDGES_UPDATED:
  case actionTypes.EDGE_DELETED:
  case actionTypes.SCENARIO_LOADED:
    return action.edges
  default:
    return state
  }
}

const waterLevel = (state = 1, action) => {
  switch(action.type) {
  case actionTypes.UPDATE_WATER_LEVEL:
  case actionTypes.DATA_IMPORTED:
  case actionTypes.SCENARIO_LOADED:
    return action.waterLevel
  default:
    return state
  }
}

const selected = (state = {}, action) => {
  switch(action.type) {
  case actionTypes.EDGE_SELECTED:
    return {
      edgeId: action.edgeId
    }
  case actionTypes.VERTEX_SELECTED:
    return {
      vertexId: action.vertexId
    }
  case actionTypes.EDGE_ADDED:
  case actionTypes.CANCELED:
  case actionTypes.EDGE_DELETED:
  case actionTypes.START_RUNNING_SIMULATION:
  case actionTypes.SIMULATION_LOADED:
    return {}

  default:
    return state
  }
}

const hovered = (state = {}, action) => {
  switch(action.type) {
  case actionTypes.EDGE_HOVERED:
    return {
      edgeId: action.edgeId
    }
  case actionTypes.VERTEX_HOVERED:
    return {
      vertexId: action.vertexId
    }
  case actionTypes.EDGE_DELETED:
  case actionTypes.START_RUNNING_SIMULATION:
  case actionTypes.SIMULATION_LOADED:
    return {}

  default:
    return state
  }
}

const simulationStatus = (state = {}, action) => {
  switch(action.type) {
  case actionTypes.START_RUNNING_SIMULATION:
    const { simulationSettings = {} } = action
    return {
      cancelingSimulation: false,
      runningSimulation: true,
      playingSimulation: true,
      simulationStep: 0,
      timeStep: simulationSettings.timeStep,
      showForces: [forceTypes.total]
    }

  case actionTypes.FINISHED_RUNNING_SIMULATION:
    return {
      ...state,
      runningSimulation: false,
      cancelingSimulation: false
    }

  case actionTypes.CANCELING_SIMULATION:
    return {
      ...state,
      cancelingSimulation: true
    }

  case actionTypes.CHANGE_SIMULATION_STEP:
    return {
      ...state,
      simulationStep: action.simulationStep
    }

  case actionTypes.SIMULATION_ENDED:
    return {
      ...state,
      playingSimulation: false,
      simulationStep: null
    }

  case actionTypes.SHOW_FORCE_TOGGLED:
    return {
      ...state,
      showForces: toggleShowForce(state.showForces, action.forceType)
    }

  case actionTypes.SIMULATION_STEP_CHANGED:
    return {
      ...state,
      simulationStep: action.simulationStep
    }

  default:
    return state
  }
}

const initialSimulationResultsState = {
  vertexPositions: [],
  forces: [],
  waterLevel: 0,
  totalSteps: 0
}

const simulationResults = (state = initialSimulationResultsState, action) => {
  switch(action.type) {
  case actionTypes.START_RUNNING_SIMULATION:
    return action.simulationResults

  case actionTypes.SIMULATION_RESULTS_RECEIVED:
    return {
      ...state,
      vertexPositions: [
        ...state.vertexPositions,
        ...action.vertexPositions
      ],
      forces: [
        ...state.forces,
        ...action.forces
      ],
      waterLevel: [
        ...state.waterLevel,
        ...action.waterLevel
      ],
      totalSteps: action.totalSteps
    }

  case actionTypes.SIMULATION_ENDED:
    return initialSimulationResultsState

  default:
    return state
  }
}

const addMode = (state = {}, action) => {
  switch(action.type) {
  case actionTypes.ADD_MODE_ENTERED:
    return {
      adding: true,
      addingEdgeType: action.edgeType,
      firstVertexType: action.firstVertexType
    }

  case actionTypes.FIRST_VERTEX_SET:
    return {
      ...state,
      firstVertex: action.firstVertex,
      firstVertexType: action.firstVertexType,
      firstVertexId: action.firstVertexId,
      firstVertexEdgeId: action.firstVertexEdgeId
    }

  case actionTypes.EDGE_ADDED:
  case actionTypes.CANCELED:
    return { adding: false }

  default:
    return state
  }
}

const reducer = combineReducers({
  vertices,
  edges,
  selected,
  hovered,
  waterLevel,
  addMode,
  simulationStatus,
  simulationResults
})

export default reducer
