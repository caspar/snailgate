import ReactDOM from 'react-dom'
import React from 'react'
import App from './components/App'

const render = Component => {
  ReactDOM.render(
    <Component />,
    document.getElementById('main')
  )
}

render(App)

if (module.hot) // thanks webpack
  module.hot.accept('./components/App', () => {
    render(App)
  })
