import React, { Component } from 'react'
import Gui from './Gui'
import SnailGateElements from './SnailGateElements'
import DataImporterExporter from './DataImporterExporter'
import Scenarios from './Scenarios'
import SceneEditorControls from './SceneEditorControls'
import SimulationController from './SimulationController'
import SimulationPlayer from './SimulationPlayer'

import { fromSimulationData } from 'models'
import { scenarioLoaded } from '../actions'
import { connect, Provider } from 'react-redux'
import store from '../store'

const fontFamily = 'Tahoma, Geneva, sans-serif'

const App = () => (
  <div style={{fontFamily}}>
    <Gui/>
    <h1>Snailgate</h1>
    <SnailGateElements />
    <SceneEditorControls />
    <SimulationPlayer />
    <SimulationController />
    <Scenarios />
    <DataImporterExporter />
  </div>
)


const getScenarioSimulationData = () => {
  if (!window.scenarioJson) return

  return fromSimulationData(window.scenarioJson)
}

class AppContainer extends Component {
  componentWillMount() {
    const scenarioJson = getScenarioSimulationData()

    if(scenarioJson)
      this.props.dispatch(scenarioLoaded(scenarioJson))
  }

  render() {
    return <App />
  }
}

const ConnectedAppContainer = connect()(AppContainer)

const AppContainerWithProvider = () => (
  <Provider store={store}>
    <ConnectedAppContainer />
  </Provider>
)

export default AppContainerWithProvider
