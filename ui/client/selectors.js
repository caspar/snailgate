import { isNumber } from 'lodash'

export const waterLevel = state => {
  if (isSimulating(state))
    return state.simulationResults.waterLevel[simulationStep(state)] || state.waterLevel
  return state.waterLevel
}

export const vertices = state => {
  if (playingSimulation(state))
    return state.simulationResults.vertices

  return state.vertices
}

export const availableSimulationSteps = state => {
  if (!isSimulating(state)) return

  return state.simulationResults.vertexPositions.length
}

export const totalSteps = state => {
  if (!isSimulating(state)) return

  return state.simulationResults.totalSteps
}

export const simulatedVertexPositions = state => {
  if (!isSimulating(state)) return

  return state.simulationResults.vertexPositions[simulationStep(state)]
}

export const simulatedForces = state => {
  if (!isSimulating(state)) return

  return state.simulationResults.forces[simulationStep(state)]
}

export const isAddingEdge = ({ addMode }) => addMode.adding

export const onFirstVertex = ({ addMode }) => !addMode.firstVertex

export const onSecondVertex = state => !onFirstVertex(state)

export const hasEdgeSelected = ({ selected }) => isNumber(selected.edgeId)

export const edges = state => {
  if (playingSimulation(state))
    return state.simulationResults.edges
  return state.edges
}

export const edgeBeingAdded = state => {
  if (isAddingEdge(state) && onSecondVertex(state)) {
    return {
      startP: state.addMode.firstVertex,
      type: state.addMode.addingEdgeType
    }
  }
}

export const showForces = ({ simulationStatus }) => simulationStatus.showForces

export const selectedVertexId = ({ selected }) => selected.vertexId

export const selectedEdgeId = ({ selected }) => selected.edgeId

export const firstVertexId = ({ addMode }) => addMode.firstVertexId

export const hoveredEdgeId = ({ hovered }) => hovered.edgeId

export const hoveredVertexId = ({ hovered }) => hovered.vertexId

export const playingSimulation = ({ simulationStatus }) => simulationStatus.playingSimulation

export const cancelingSimulation = ({ simulationStatus }) => simulationStatus.cancelingSimulation

export const simulationStep = ({ simulationStatus }) => simulationStatus.simulationStep

export const runningSimulation = ({ simulationStatus }) => simulationStatus.runningSimulation

export const simulationTimeStep = ({ simulationStatus }) => simulationStatus.timeStep

export const isSimulating = playingSimulation

export const isEditing = state => !isSimulating(state)
