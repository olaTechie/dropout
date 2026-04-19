import { Component } from 'react';

// Minimal error boundary scoped to the WebGL canvas. If anything inside
// the R3F tree throws (e.g. shader compile failure, blocked external
// asset, GPU lost), we log to console and unmount the canvas so the
// surrounding HTML (scrollama text, HUD overlays) stays usable instead
// of the whole route blanking.
export default class CanvasErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  componentDidCatch(error, info) {
    // eslint-disable-next-line no-console
    console.error('Canvas error boundary caught:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="fixed inset-0 -z-0 flex items-center justify-center text-muted text-sm pointer-events-none">
          (3D scene unavailable — falling back to text view)
        </div>
      );
    }
    return this.props.children;
  }
}
