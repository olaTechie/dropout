export function hasWebGL() {
  try {
    const canvas = document.createElement('canvas');
    return !!(window.WebGLRenderingContext && (canvas.getContext('webgl2') || canvas.getContext('webgl')));
  } catch {
    return false;
  }
}

// @react-three/postprocessing requires WebGL2; without it EffectComposer
// throws at construction. Use this to gate <Effects /> so we degrade to
// the unprocessed scene rather than crashing the whole canvas.
export function hasWebGL2() {
  try {
    const canvas = document.createElement('canvas');
    return !!(window.WebGL2RenderingContext && canvas.getContext('webgl2'));
  } catch {
    return false;
  }
}
