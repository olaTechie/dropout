import { Component } from 'react';

// Minimal error boundary scoped to the WebGL canvas. If anything inside
// the R3F tree throws (e.g. shader compile failure, blocked external
// asset, GPU lost), we surface the error message in the fallback UI
// (so the user can report it without DevTools) and unmount the canvas
// so the surrounding HTML (scrollama text, HUD overlays) stays usable
// instead of the whole route blanking.
export default class CanvasErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, errorMessage: '' };
  }

  static getDerivedStateFromError(error) {
    return {
      hasError: true,
      errorMessage: `${error?.name || 'Error'}: ${error?.message || String(error)}`,
    };
  }

  componentDidCatch(error, info) {
    // eslint-disable-next-line no-console
    console.error('Canvas error boundary caught:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className={this.props.className || 'flex min-h-[320px] flex-col items-center justify-center text-muted text-sm px-6 text-center'}>
          <div className="mb-2">3D scene unavailable — falling back to text view.</div>
          <div className="text-xs opacity-60 max-w-md font-mono break-words">
            {this.state.errorMessage}
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
