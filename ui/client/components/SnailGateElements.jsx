import React, { Component } from 'react'
import { map, round, isNumber } from 'lodash'
import { edgeTypes, forceColors } from 'models'
import { ReactSVGPanZoom } from 'react-svg-pan-zoom'
import { getCentroid, getNormal, getLength } from '../utils/geometry'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import * as actions from '../actions'
import * as selectors from '../selectors'
import Water from './Water'
import { floorSize, visualScale, width, height, toSvgX, toSvgY, fromSvgX, fromSvgY } from '../utils/svg'

const sceneSize = 10000

const wrapperStyle = {
  width,
  height,
  border: 'black 1px solid'
}

// color scheme: http://colorpalettes.net/wp-content/uploads/2014/01/cvetovaya-palitra-205.jpg

const floorColor = '#DCAB5E'

const vertexActiveColor = 'red'

const edgeColors = {
  [edgeTypes.rod]: 'black',
  [edgeTypes.rope]: '#AB420C'
}

const activeEdgeColors = {
  [edgeTypes.rod]: vertexActiveColor,
  [edgeTypes.rope]: vertexActiveColor
}

const emptyFn = () => {}

const EdgeDrawingAide = ({ pa, pb, length }) => {
  const centroid = getCentroid(pa, pb)
  let normal = getNormal(pa, pb)

  // flip normal if edge order is flipped
  if (pa[0] > pb[0])
    normal = [-normal[0], -normal[1]]

  const offsetPos = [centroid[0] + normal[0] * 0.1, centroid[1] + normal[1] * 0.1]

  const pos = [toSvgX(offsetPos[0]), toSvgY(offsetPos[1])]

  return (
    <g transform={`rotate(${getSvgRotation(normal) + 90} ${pos[0]} ${pos[1]})`}>
      <text textAnchor='middle' x={pos[0]} y={pos[1]} >
        {`${round(length, 2)} m`}
      </text>
    </g>
  )
}


const Splitvertices = ({ pa, pb, splitSize, onClick, onMouseOver, onMouseOut }) => {
  const edgeLength = getLength(pa, pb)
  const vertexSize = 1
  const edgeSize = edgeLength / splitSize
  const gap = edgeSize * visualScale - vertexSize
  return (
    <line
      x1={toSvgX(pa[0])}
      y1={toSvgY(pa[1])}
      x2={toSvgX(pb[0])}
      y2={toSvgY(pb[1])}
      strokeWidth={6}
      stroke={edgeColors[edgeTypes.rod]}
      strokeLinecap='round'
      strokeDasharray={`${vertexSize}, ${gap}`}
      onClick={onClick}
      onMouseOver={onMouseOver}
      onMouseOut={onMouseOut}
    />
  )
}

const toCurvedLineArgs = (pa, pb, lengthDiff) => {
  const centroid = getCentroid(pa, pb)
  const middleSag = centroid[1] - lengthDiff

  return `M${toSvgX(pa[0])} ${toSvgY(pa[1])} Q ${toSvgX(centroid[0])} ${toSvgY(middleSag)} ${toSvgX(pb[0])} ${toSvgY(pb[1])}`
}

const Edge = ({ edgeType, length, isNew, id, pa, pb, edgeClicked, edgeHovered = emptyFn, active, splitSize = 1 }) => {
  const commonProps = {
    strokeWidth:'4',
    stroke: active ? activeEdgeColors[edgeType] : edgeColors[edgeType],
    onClick: () => edgeClicked(id),
    onMouseOver: () => edgeHovered(id, true),
    onMouseOut: () => edgeHovered(id, false)
  }

  const lengthBetweenvertices = getLength(pa, pb)

  let lineElement

  if (edgeType !== edgeTypes.rope || length === lengthBetweenvertices)
    lineElement = (
      <line
        x1={toSvgX(pa[0])}
        y1={toSvgY(pa[1])}
        x2={toSvgX(pb[0])}
        y2={toSvgY(pb[1])}
        {...commonProps}
      />
    )
  else
    lineElement = (
      <path
        d={toCurvedLineArgs(pa, pb, length - lengthBetweenvertices)}
        {...commonProps}
        fill='transparent'
      />
    )

  return (
    <g>
      {lineElement}
      {(isNew || active) && (
        <EdgeDrawingAide pa={pa} pb={pb} length={length} />
      )}
      {splitSize > 1 && <Splitvertices {...commonProps} pa={pa} pb={pb} splitSize={splitSize} />}
    </g>
  )
}

const toDegrees = radians => radians * 180 / Math.PI

const getDirection = y => y < 0 ? 1 : -1

const dot = ([x1, y1], [x2, y2]) => [x1 * x2 + y1 * y2]
const getSvgRotation = normalized => toDegrees(Math.acos(dot(normalized, [1, 0]))) * getDirection(normalized[1])

const forceVisScale = 1/10

const Force = ({ origin, force, type }) => {
  const originX = toSvgX(origin[0])
  const originY = toSvgY(origin[1])
  const length = Math.sqrt(Math.pow(force[0], 2) + Math.pow(force[1], 2))
  const normalized = [force[0] / length, force[1] / length]
  const endX = originX + length * forceVisScale

  return (
    <g transform={`rotate(${getSvgRotation(normalized)} ${originX} ${originY})`} >
      <line x1={originX} y1={originY} x2={endX} y2={originY} strokeWidth='2' stroke={forceColors[type]} />
      <polygon points={`${endX},${originY+5} ${endX},${originY-5} ${endX+5},${originY}`} fill={forceColors[type]} />
    </g>
  )
}

const Vertex = ({ id, point, boyantRadius = 0, showForces, force, vertexClicked, vertexHovered, active }) => {
  const commonProps = {
    onClick: () => vertexClicked(id),
    onMouseOver: () => vertexHovered(id, true),
    onMouseOut: () => vertexHovered(id, false)
  }

  return (
    <g>
      {boyantRadius === 0 && (
        <circle
          cx={toSvgX(point[0])}
          cy={toSvgY(point[1])}
          r='2'
          style={{
            fill: active ? vertexActiveColor : 'black'
          }}
          {...commonProps}
        />
      )}
      {boyantRadius > 0 && (
        <circle
          cx={toSvgX(point[0])}
          cy={toSvgY(point[1])}
          fill={active ? vertexActiveColor : 'black'}
          r={boyantRadius * visualScale}
          style={{
            fill: active ? vertexActiveColor: 'rgba(0, 0, 0, 0)',
            strokeWidth: 0.5,
            stroke: 'black'
          }}
          {...commonProps}
        />
      )}
      {force && map(showForces, forceType => (
        <Force key={forceType} origin={point} force={force[forceType]} type={forceType} />
      ))}
    </g>
  )
}

const Floor = ({ floorClicked }) => (
  <rect fill={floorColor} width={sceneSize} x={-sceneSize/2} height={sceneSize / 2} y={height - (floorSize * visualScale)} onClick={floorClicked} />
)

const getVertexPosition = (vertexId, vertices, movedVertex, simulatedVertexPositions) => (
  getVertexPoint(simulatedVertexPositions, vertices[vertexId], movedVertex, vertexId)
)

const Edges = ({edges, vertices, movedVertex, simulatedVertexPositions, edgeClicked, edgeHovered, selectedEdgeId, hoveredEdgeId }) => (
  <g>
    {map(edges, (edge, i) => (
      <Edge
        key={i}
        id={i}
        edgeType={edge.type}
        length={edge.length}
        splitSize={edge.splitSize}
        pa={getVertexPosition(edge.v[0], vertices, movedVertex, simulatedVertexPositions)}
        pb={getVertexPosition(edge.v[1], vertices, movedVertex, simulatedVertexPositions)}
        edgeClicked={edgeClicked}
        edgeHovered={edgeHovered}
        active={selectedEdgeId === i || hoveredEdgeId === i}
      />
    ))}
  </g>
)

const getVertexPoint = (simulatedVertexPositions, vertex, movedVertex, i) => {
  if (simulatedVertexPositions) return simulatedVertexPositions[i]
  if (movedVertex && movedVertex.id === i) return movedVertex.p
  return vertex.p
}

const vertices = ({ vertices, movedVertex, showForces, vertexClicked, simulatedVertexPositions, simulatedForces, vertexHovered, firstVertexId, hoveredVertexId, selectedVertexId }) => (
  <g>
    {map(vertices, (vertex, i) => (
      <Vertex
        key={i}
        id={i}
        point={getVertexPoint(simulatedVertexPositions, vertex, movedVertex, i)}
        boyantRadius={vertex.boyantRadius}
        vertexClicked={vertexClicked}
        vertexHovered={vertexHovered}
        showForces={showForces}
        force={simulatedForces ? simulatedForces[i] : null}
        active={i === firstVertexId || i === hoveredVertexId || i === selectedVertexId}
      />
    ))}
  </g>
)

// list of codes: https://www.cambiaresearch.com/articles/15/javascript-char-codes-key-codes
const ESCAPE = 27
const D = 68

class SnailGateElements extends Component {
  constructor(props, context) {
    super(props, context)
    this.Viewer = null

    this.updateMouseCoords = this.updateMouseCoords.bind(this)
    this.edgeClicked = this.edgeClicked.bind(this)
    this.floorClicked = this.floorClicked.bind(this)
    this.emptySpaceClicked = this.emptySpaceClicked.bind(this)
    this.keyPress = this.keyPress.bind(this)
    this.onMouseDown = this.onMouseDown.bind(this)
    this.onMouseUp = this.onMouseUp.bind(this)

    this.state = {
      mouse: [0, 0]
    }
  }

  componentDidMount() {
    this.Viewer.fitToViewer()

    document.addEventListener('keydown', this.keyPress, false)
  }

  keyPress(e) {
    const { keyCode } = e
    switch(keyCode) {
    case ESCAPE:
      e.preventDefault()
      this.props.cancel()
      break
    case D:
      this.props.tryDeleteSelectedEdge()
      break
    default:
      break
    }
  }

  updateMouseCoords({ x, y}) {
    this.setState({
      mouse: [fromSvgX(x), fromSvgY(y)]
    })
  }

  edgeClicked(edgeId){
    this.props.edgeClicked(edgeId, this.state.mouse)
  }

  floorClicked() {
    this.props.floorClicked(this.state.mouse)
  }

  emptySpaceClicked() {
    this.props.emptySpaceClicked(this.state.mouse)
  }

  get newEdge() {
    const { edgeBeingAdded } = this.props
    if (edgeBeingAdded) {
      const points = [edgeBeingAdded.startP, this.state.mouse]
      return {
        v: [{p: points[0]}, {p: points[1]}],
        type: edgeBeingAdded.type,
        length: getLength(points[0], points[1])
      }
    }
  }

  onMouseDown() {
    if (this.props.isEditing && isNumber(this.props.hoveredVertexId))
      this.setState({
        movingVertexId: this.props.hoveredVertexId
      })
  }

  onMouseUp() {
    if (isNumber(this.state.movingVertexId)) {
      this.props.moveVertex(this.state.movingVertexId, this.state.mouse)
      this.setState({
        movingVertexId: null
      })
    }
  }

  get movedVertex() {
    if (!isNumber(this.state.movingVertexId)) return

    return {
      id: this.state.movingVertexId,
      p: this.state.mouse
    }
  }

  render() {
    const {
      /* state */
      edges,
      selectedEdgeId,
      vertices,
      firstVertexId,
      waterLevel,
      hoveredEdgeId,
      hoveredVertexId,
      selectedVertexId,
      simulatedVertexPositions,
      simulatedForces,
      showForces,

      vertexClicked,
      vertexHovered,
      edgeHovered
    } = this.props

    const newEdge = this.newEdge

    return (
      <div style={wrapperStyle}>
        <ReactSVGPanZoom
          style={{outline: '1px solid black'}}
          preventPanOutside
          detectAutoPan={false}
          detectWheel={false}
          width={width} height={height} ref={Viewer => {this.Viewer = Viewer}} onMouseMove={this.updateMouseCoords} onMouseDown={this.onMouseDown} onMouseUp={this.onMouseUp}
        >
          <svg width={width} height={height} >
            <rect width={sceneSize} height={sceneSize} x={-sceneSize/2} y={-sceneSize/2} onClick={this.emptySpaceClicked} fill='#fff' />
            <Water level={waterLevel} vertices={vertices} edges={edges} simulatedVertexPositions={simulatedVertexPositions} />
            <Floor floorClicked={this.floorClicked} />
            {newEdge && (
              <Edge isNew edgeType={newEdge.type} pa={newEdge.v[0].p} pb={newEdge.v[1].p} length={newEdge.length} selectedEdgeId={selectedEdgeId} edgeClicked={this.emptySpaceClicked} />
            )}
            <Edges edges={edges} vertices={vertices} movedVertex={this.movedVertex} simulatedVertexPositions={simulatedVertexPositions} edgeClicked={this.edgeClicked} edgeHovered={edgeHovered} selectedEdgeId={selectedEdgeId} hoveredEdgeId={hoveredEdgeId} />
            <vertices vertices={vertices} movedVertex={this.movedVertex} simulatedVertexPositions={simulatedVertexPositions} showForces={showForces} simulatedForces={simulatedForces} vertexClicked={vertexClicked} vertexHovered={vertexHovered} vertexMouseDowned={this.vertexMouseDowned} firstVertexId={firstVertexId} hoveredVertexId={hoveredVertexId} selectedVertexId={selectedVertexId} />
          </svg>
        </ReactSVGPanZoom>
      </div>
    )
  }
}

const mapStateToProps = state => ({
  edges: selectors.edges(state),
  selectedEdgeId: selectors.selectedEdgeId(state),
  vertices: selectors.vertices(state),
  firstVertexId: selectors.firstVertexId(state),
  waterLevel: selectors.waterLevel(state),
  hoveredEdgeId: selectors.hoveredEdgeId(state),
  hoveredVertexId: selectors.hoveredVertexId(state),
  selectedVertexId: selectors.selectedVertexId(state),
  simulatedVertexPositions: selectors.simulatedVertexPositions(state),
  simulatedForces: selectors.simulatedForces(state),
  showForces: selectors.showForces(state),
  edgeBeingAdded: selectors.edgeBeingAdded(state),
  isEditing: selectors.isEditing(state)
})

const mapDispatchToProps = dispatch => (
  bindActionCreators(actions, dispatch)
)

export default connect(mapStateToProps, mapDispatchToProps)(SnailGateElements)
