import { Component } from 'react'
import { GUI } from 'dat-gui'
import { connect } from 'react-redux'
import { updateWaterLevel } from '../actions'

class Gui extends Component {
  constructor(props) {
    super(props)

    this.state = {
      waterLevel: props.waterLevel
    }
  }
  componentDidMount() {
    this.gui = new GUI()

    this.gui.add(this.state, 'waterLevel').min(0).max(5).onChange(waterLevel => {
      this.props.dispatch(updateWaterLevel(waterLevel))
    })
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.waterLevel !== this.props.waterLevel) {
      this.gui.waterLavel = nextProps.waterLevel
    }
  }

  render() {
    return null
  }
}

const mapStateToProps = state => ({
  waterLevel: state.waterLevel
})

export default connect(mapStateToProps)(Gui)
