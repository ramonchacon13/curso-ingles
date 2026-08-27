import { Component } from 'react'

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props)
    this.state = { error: null }
  }

  static getDerivedStateFromError(error) {
    return { error }
  }

  componentDidCatch(error, info) {
    console.error('App crash:', error, info)
  }

  render() {
    if (this.state.error) {
      return (
        <div className="auth-page" style={{ padding: 24 }}>
          <h2>Algo salió mal</h2>
          <pre style={{ whiteSpace: 'pre-wrap', color: '#f87171' }}>
            {this.state.error.message}
          </pre>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12, opacity: 0.7 }}>
            {this.state.error.stack}
          </pre>
        </div>
      )
    }
    return this.props.children
  }
}
