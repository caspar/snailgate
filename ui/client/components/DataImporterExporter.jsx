import React, { Component } from 'react'
import { toSimulationData } from 'models'
import * as selectors from '../selectors'
import * as actions from '../actions'
import { bindActionCreators } from 'redux'
import { connect } from 'react-redux'

class DataImporterExporter extends Component {
  constructor(props) {
    super(props)

    this.selectAll = this.selectAll.bind(this)
  }

  selectAll(e) {
    e.preventDefault()

    this.textarea.select()
  }
  

  render() {
    const { contents, onChange, importJson } = this.props
    
    return (
      <div style={{ marginTop: '20px '}}>
        <h2>Data Representation</h2>
        <form>
          <button type='button' onClick={this.selectAll}>Select All</button>
          <button type='button' onClick={importJson}>Apply Json</button>
          <br/>
          <textarea value={contents} onChange={e => { console.log('handling'); onChange(e) }} cols={100} rows={50} ref={textarea => { this.textarea = textarea }}/>
        </form> 
      </div>
    )
  }
}

const toSimulationDataJson = props => (
  JSON.stringify(toSimulationData(
    props.vertices,
    props.edges,
    props.waterLevel
  ), null, 2)
)

class DataImporterExporterContainer extends Component {
  constructor(props) {
    super(props)

    this.state = {
      contents: toSimulationDataJson(props)
    }
    
    this.onChange = this.onChange.bind(this)
    this.importJson = this.importJson.bind(this)
  }

  componentWillReceiveProps(nextProps) {
    if (
      nextProps.vertices !== this.props.vertices 
      || nextProps.edges !== this.props.edges
      || nextProps.waterLevel !== this.props.waterLevel
    )
      this.setState({
        contents: toSimulationDataJson(nextProps)
      })
  }

  importJson() {
    this.props.importData(JSON.parse(this.state.contents))
  }

  onChange(e) {
    this.setState({
      contents: e.target.value
    })
  }

  render() {
    return (
      <DataImporterExporter 
        {...this.state} 
        open={this.open}
        close={this.open}
        onChange={this.onChange}
        importJson={this.importJson}
      />
    )
  }
}

const mapStateToProps = state => ({
  vertices: selectors.vertices(state),
  edges: selectors.edges(state),
  waterLevel: selectors.waterLevel(state)
})

const mapDispatchToProps = dispatch => (
  bindActionCreators(actions, dispatch)
)

export default connect(mapStateToProps, mapDispatchToProps)(DataImporterExporterContainer)
