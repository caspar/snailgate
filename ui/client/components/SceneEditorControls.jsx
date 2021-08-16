import React from 'react'
import { isNumber } from 'lodash'
import { edgeTypes, vertexTypes } from 'models'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import * as actions from '../actions'
import * as selectors from '../selectors'

const SelectedEdge = ({ selectedEdge, splitSelectedEdge, changeEdgeLength }) => {
  if (selectedEdge.type === edgeTypes.spring)
    return (
      <label>
        Split into
        <input type='number' onChange={e => splitSelectedEdge(parseInt(e.target.value))} style={{width: 50}} value={selectedEdge.splitSize || 1} />
        edges
      </label>
    )
  
  if (selectedEdge.type === edgeTypes.rope)
    return (
      <label>
        Fully extended rope length 
        <input type='number' value={selectedEdge.length} onChange={e => changeEdgeLength(Number(e.target.value))} style={{width: 100}} step='0.1' />
      </label>
    )
  return null
}

const getBoyantVolumeFromCheckedValue = value => value ? 0.1 : 0

const SelectedVertex = ({ selectedVertex, changeVertexBoyancy, changeVertexFixed }) => (
  <span>
    <label>
      Fixed 
      <input type='checkbox' checked={selectedVertex.type === vertexTypes.fixed} onChange={e => changeVertexFixed(e.target.checked)} />
    </label>
    <label>
      Boyant
      <input type='checkbox' checked={selectedVertex.boyantRadius > 0} onChange={e => changeVertexBoyancy(getBoyantVolumeFromCheckedValue(e.target.checked))} />
    </label>
    {selectedVertex.boyantRadius >= 0 && (
      <label>
        &nbsp;Bouy Radius&nbsp;
        <input type='number' value={selectedVertex.boyantRadius} onChange={e => changeVertexBoyancy(Number(e.target.value))} style={{width: 50}} step='0.01'/>
      </label>
    )}
  </span>
)

const SceneEditorControls = props => {
  if (props.playingSimulation) return null

  return (
    <div>
      {!isNumber(props.selectedEdgeId) && (
        <div>
          <button type='button' onClick={() => props.enterAddMode(edgeTypes.rod)} disabled={props.isAddingEdge} >
            Add Spring
          </button>

          {props.edges.length > 0 && (
            <button type='button' onClick={() => props.enterAddMode(edgeTypes.rope)} disabled={props.isAddingEdge} >
              Add Rope
            </button>
          )}
        </div>
      )}

      {isNumber(props.selectedEdgeId) && (
        <SelectedEdge selectedEdge={props.edges[props.selectedEdgeId]} splitSelectedEdge={props.splitSelectedEdge} changeEdgeLength={props.changeEdgeLength} />
      )}
      {isNumber(props.selectedVertexId) && (
        <SelectedVertex selectedVertex={props.vertices[props.selectedVertexId]} changeVertexBoyancy={props.changeVertexBoyancy} changeVertexFixed={props.changeVertexFixed} />
      )}
    </div>
  )
}

const mapStateToProps = state => ({
  playingSimulation: selectors.playingSimulation(state),
  selectedEdgeId: selectors.selectedEdgeId(state),
  selectedVertexId: selectors.selectedVertexId(state),
  isAddingEdge: selectors.isAddingEdge(state),
  edges: selectors.edges(state),
  vertices: selectors.vertices(state)
})

const mapDispatchToProps = dispatch => (
  bindActionCreators(actions, dispatch)
)

export default connect(mapStateToProps, mapDispatchToProps)(SceneEditorControls)

