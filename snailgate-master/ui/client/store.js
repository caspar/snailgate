import { createStore, applyMiddleware, compose } from 'redux'
import thunk from 'redux-thunk'
import reducers from './reducers'
import { simulationResultsReceived } from './actions'
import socketClient from './socketClient'

const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose
const store = createStore(reducers, composeEnhancers(
  applyMiddleware(thunk)
))

socketClient.on('results', results => {
  store.dispatch(simulationResultsReceived(results))
})

export default store
