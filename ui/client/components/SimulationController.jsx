import React, { Component } from 'react'
import { ceil, floor } from 'lodash'
import Clock from './Clock'
import { connect } from 'react-redux'
import { bindActionCreators } from 'redux'
import * as actions from '../actions'
import * as selectors from '../selectors'

class SimulationController extends Component {
  constructor(props) {
    super(props)

    this.state = { 
      timeStep: 0.01,
      maxIterations: 10000,
      simulationMethod: 'Backward Euler',
      randomSplitVertexPositions: false,
      waterLevelRaiseRate: 0.2 
    }

    this.handleTimeStepChanged = this.handleTimeStepChanged.bind(this)
    this.handleMaxIterationsChanged = this.handleMaxIterationsChanged.bind(this)
    this.handleSimulationMethodChanged = this.handleSimulationMethodChanged.bind(this)
    this.runSimulation = this.runSimulation.bind(this)
    this.simulationDurationChanged = this.simulationDurationChanged.bind(this)
    this.setPlayDuration = this.setPlayDuration.bind(this)
    this.handleRandomSplitVertexPositionsChanged = this.handleRandomSplitVertexPositionsChanged.bind(this)
    this.handleWaterLevelRaiseRateChanged = this.handleWaterLevelRaiseRateChanged.bind(this)
  }

  handleTimeStepChanged(e) {
    this.setState({ timeStep: e.target.value })
  }

  handleMaxIterationsChanged(e) {
    this.setState({ maxIterations: e.target.value })
  }
  
  handleSimulationMethodChanged(e) {
    this.setState({ simulationMethod: e.target.value })
  }

  handleRandomSplitVertexPositionsChanged(e) {
    this.setState({ randomSplitVertexPositions: e.target.checked })
  }

  handleWaterLevelRaiseRateChanged(e) {
    this.setState({waterLevelRaiseRate: e.target.value })
  }

  setDuration(e, unit) {
    const duration = this.simulationDuration[unit](e.target.value)

    this.setState({
      maxIterations: ceil(duration.valueOf() / (this.state.timeStep * 1000))
    })
  }

  simulationDurationChanged(newDuration) {
    this.setState({
      maxIterations: ceil(newDuration / (this.timeStepMs))
    })
  }

  runSimulation() {
    this.props.runSimulation({
      timeStep: this.state.timeStep,
      maxIterations: this.state.maxIterations,
      simulationMethod: this.state.simulationMethod,
      waterLevelRaiseRate: this.state.waterLevelRaiseRate
    }, this.state.randomSplitVertexPositions)
  }

  componentWillUnmount() {
    this.stopPlaying()
  }

  componentWillReceiveProps(nextProps) {
    // autopause if on last step
    if (nextProps.simulationStep !== this.props.simulationStep)
      if (nextProps.simulationStep +1 === nextProps.availableSimulationSteps)
        this.pause()
  }

  setPlayDuration(duration) {
    const step = floor(duration / this.timeStepMs)
    this.props.setSimulationStep(step)
  }

  get timeStepMs() {
    return this.state.timeStep * 1000
  }

  get simulationDuration() {
    return this.timeStepMs * this.state.maxIterations
  }

  render() {
    const { 
      playingSimulation, 
      runningSimulation, 
      cancelingSimulation,
      isSimulating, 
      cancelSimulation,
      loadSimulationResults
    } = this.props

    return (
      <fieldset>
        <legend>Simulation</legend>
        <label>
          Load simulation results
          <input type='file' encType='multipart/form-data' onChange={e => loadSimulationResults(e.target.files)} />
        </label>
        <br />
        <label>
          Time Step&nbsp;
          <input type='number' value={this.state.timeStep} onChange={this.handleTimeStepChanged} disabled={playingSimulation} style={{width: 50}} />
          seconds
        </label>
        <br/>
        <label>
          Max Iterations&nbsp;
          <input type='number' value={this.state.maxIterations} onChange={this.handleMaxIterationsChanged} disabled={playingSimulation} style={{width: 80}} />
          &nbsp;or&nbsp;
          Simulation Duration (mm:ss:ms) &nbsp;
          <Clock duration={this.simulationDuration} onChange={this.simulationDurationChanged} disabled={playingSimulation} />
        </label>
        <br/>
        <label>
          Randomly sample split vertex positions&nbsp;
          <input type='checkbox' checked={this.state.randomSplitVertexPositions} onChange={this.handleRandomSplitVertexPositionsChanged} />
        </label>
        <br/>
        <label>
          Water level rising rate (m/s)
          <input type='number' value={this.state.waterLevelRaiseRate} onChange={this.handleWaterLevelRaiseRateChanged} step='0.1' />
        </label>
        <br/>
        <label>
          Simulation method&nbsp;
        </label>
        <select value={this.state.simulationMethod} onChange={this.handleSimulationMethodChanged} disabled={isSimulating}>
          <option>Forward Euler</option>
          <option>Backward Euler</option>
        </select>
        <button type='button' onClick={this.runSimulation} disabled={runningSimulation} >
          {!runningSimulation ? 'Run Simulation' : 'Simulation Running...'}
        </button>
        {runningSimulation && (
          <button type='button' onClick={cancelSimulation} disabled={cancelingSimulation} >
            {!cancelingSimulation ? 'Cancel Simulation' : 'Cancelin)g Simulation...'}
          </button>
        )}
      </fieldset>
    )
  }
}

const mapStateToProps = state => ({
  playingSimulation: selectors.playingSimulation(state),
  runningSimulation: selectors.runningSimulation(state), 
  cancelingSimulation: selectors.cancelingSimulation(state),
  isSimulating: selectors.isSimulating(state) 
})

const mapDispatchToProps = dispatch => (
  bindActionCreators(actions, dispatch)
)

export default connect(mapStateToProps, mapDispatchToProps)(SimulationController)
