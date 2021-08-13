import React, { Component } from 'react'
import { map, floor, round, includes } from 'lodash'
import { forceTypes, forceColors } from 'models'
import Clock from './Clock'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import * as actions from '../actions'
import * as selectors from '../selectors'

const toPercentage = val => `${round(val * 100, 2)}%`

const ShowForcesCheckboxes = ({ showForces, toggleShowForceType }) => (
  <ul>
    {map(forceTypes, forceType => (
      <li key={forceType}>
        <label style={{color: forceColors[forceType]}}>
          {forceType}
          <input
            name={forceType}
            value={forceType}
            type='checkbox'
            checked={includes(showForces, forceType)}
            onChange={e => toggleShowForceType(e.target.value)}
          />
        </label>
      </li>
    ))}
  </ul>
)

class SimulationPlayer extends Component {
  constructor(props) {
    super(props) 

    this.state = {}
    this.play = this.play.bind(this)
    this.pause = this.pause.bind(this)
    this.simulationBarClicked = this.simulationBarClicked.bind(this)
    this.setSimulationPlayTime = this.setSimulationPlayTime.bind(this)
  }

  componentWillMount() {
    this.animate()
  }

  componentWillUnmount() {
    this.stopAnimating()
  }

  componentWillReceiveProps(nextProps){
    if (nextProps.playingSimulation && !this.props.playingSimulation) {
      this.animate()
    } else if (!nextProps.playingSimulation && this.props.playingSimulation) {
      this.stopAnimating()
    }
  }

  animate() {
    if (this.state.playing) {
      this.props.advanceSimulation()
    }
    
    this.animationFrame = requestAnimationFrame(() => this.animate())
  }

  stopAnimating() {
    if(this.animationFrame)
      window.cancelAnimationFrame(this.animationFrame)
  }

  play() {
    if (!this.state.playing)
      this.setState({ playing: true })
  }

  simulationBarClicked(evt) {
    const e = evt.target
    const dim = e.getBoundingClientRect()
    const x = evt.clientX - dim.left

    const clickPercentage = x / (dim.right - dim.left) 

    this.props.setSimulationPercentage(clickPercentage)
  }

  pause() {
    this.setState({ playing: false })
  }

  setSimulationPlayTime(newPlayTime) {
    const step = Math.floor(newPlayTime / (this.props.simulationTimeStep * 1000))

    this.props.setSimulationStep(step)
  }

  get playPercentage() {
    return this.props.simulationStep / this.props.totalSteps
  }

  get playDuration() {
    const totalSimulationTime = this.props.totalSteps * this.props.simulationTimeStep * 1000
    return floor(this.playPercentage * totalSimulationTime)
  }

  render() {
    const { 
      playingSimulation,
      simulationStep,
      runningSimulation,
      totalSteps,
      availableSimulationSteps,
      showForces,
      advanceSimulation,
      rewindSimulation,

      endSimulation,
      setSimulationStep,
      saveSimulationResults,
      toggleShowForceType
    } = this.props

    if (!playingSimulation) return null
    
    return (
      <fieldset style={{width: 600}}>
        <legend>Simulation Playback</legend>
        <svg style={{width: '100%', height: 10}}>
          <rect width={'100%'} height={10} rx={5} ry={5} fill='#BABABA' />
          <rect width={toPercentage(availableSimulationSteps / totalSteps)} height={10} rx={5} ry={5} fill='#D8D8D8' />
          <rect width={toPercentage(this.playPercentage)} height={10} rx={5} ry={5} fill='#FFCC00' />
          <rect width={'100%'} height={10} rx={5} ry={5} opacity={0} onClick={this.simulationBarClicked} style={{cursor: 'pointer'}} />
        </svg>
        <button type='button' onClick={() => setSimulationStep(0)} >
          &lt;&lt;
        </button>
        <button type='button' onClick={rewindSimulation} disabled={this.state.playing} >
          &lt;
        </button>
        {!this.state.playing && (
          <button type='button' onClick={this.play} >
            &#x25B9;
          </button>
        )}
        {this.state.playing && (
          <button type='button' onClick={this.pause} >
            =
          </button>
        )}
        <button type='button' onClick={advanceSimulation} disabled={this.state.playing} >
          &gt;
        </button>
        <button type='button' onClick={() => setSimulationStep(availableSimulationSteps)}>
          &gt;&gt;
        </button>
        <br/>
        Simulation Time Elapsed(mm:ss:ms) &nbsp;
        <Clock duration={this.playDuration} onChange={this.setSimulationPlayTime} />
        &nbsp;
        <br />
        <label>
          Step
          <input type='number' value={simulationStep} style={{width: 90}} onChange={e => setSimulationStep(parseInt(e.target.value))}/>
          {`of ${availableSimulationSteps - 1}`}
        </label>
        <br /> 
        Show forces:
        <ShowForcesCheckboxes showForces={showForces} toggleShowForceType={toggleShowForceType} />
        <button type='button' onClick={saveSimulationResults}>
          Save Simulation Results
        </button>
        <button type='button' onClick={endSimulation} disabled={runningSimulation} >
          End Simulation
        </button>
      </fieldset>
    )
  }
}

const mapStateToProps = state => ({
  playingSimulation: selectors.playingSimulation(state),
  simulationStep: selectors.simulationStep(state),
  runningSimulation: selectors.runningSimulation(state),
  totalSteps: selectors.totalSteps(state),
  availableSimulationSteps: selectors.availableSimulationSteps(state),
  simulationTimeStep: selectors.simulationTimeStep(state),
  showForces: selectors.showForces(state)
})

const mapDispatchToProps = dispatch => (
  bindActionCreators(actions, dispatch)
)

export default connect(mapStateToProps, mapDispatchToProps)(SimulationPlayer)
