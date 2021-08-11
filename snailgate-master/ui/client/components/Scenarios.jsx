import React, { Component } from 'react'
import { map } from 'lodash'

const getFontWeight = (currentScenario, scenario) => (
  scenario === currentScenario ? 'bold': 'default'
)

const Scenarios = ({ currentScenario, scenarios }) => (
  <fieldset style={{width: 400}}>
    <legend>Scenarios</legend>
    <ul>
      {map(scenarios, (scenario, i) => (
        <li key={i} style={{fontWeight: getFontWeight(currentScenario, scenario)}}><a href={`/?scenario=${scenario}`}>{ scenario }</a></li>
      ))}
    </ul>
  </fieldset>
)


export default class ScenariosContainer extends Component {
  constructor(props) {
    super(props)

    this.state = {
      currentScenario: window.scenario,
      scenarios: window.scenarios
    }
  }

  render() {
    return <Scenarios {...this.state} />
  }
}
