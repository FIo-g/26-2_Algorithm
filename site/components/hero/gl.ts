import { NEVER } from "./data";

export type Renderer = {
  draw(clock: number, method: number, ghost: number): void;
  setDim(unlit: number, ghost: number): void; // alpha of roads not reached yet, and of the previous method's roads
  resize(): void;
  dispose(): void;
};

// Colours on the blue field are premultiplied white: unlit and ghost (lit under the previous method) alphas are set by
// setDim (16% and 42% by default), lit is 100%.
const VERT = `#version 300 es
in vec2 aPos;
in float aRank;
in float aGhost;
uniform float uClock;
uniform float uNever;
uniform float uUnlit;
uniform float uGhostAlpha;
out float vAlpha;
void main() {
  gl_Position = vec4(aPos.x * 2.0 - 1.0, 1.0 - aPos.y * 2.0, 0.0, 1.0);
  vAlpha = aRank < uClock ? 1.0 : (aGhost < uNever ? uGhostAlpha : uUnlit);
}`;

const FRAG = `#version 300 es
precision mediump float;
in float vAlpha;
out vec4 outColor;
void main() { outColor = vec4(vAlpha, vAlpha, vAlpha, vAlpha); }`;

function compile(gl: WebGL2RenderingContext, type: number, source: string): WebGLShader | null {
  const shader = gl.createShader(type);
  if (!shader) return null;
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (gl.getShaderParameter(shader, gl.COMPILE_STATUS)) return shader;
  gl.deleteShader(shader);
  return null;
}

function link(gl: WebGL2RenderingContext): WebGLProgram | null {
  const vert = compile(gl, gl.VERTEX_SHADER, VERT);
  const frag = compile(gl, gl.FRAGMENT_SHADER, FRAG);
  const program = gl.createProgram();
  if (!vert || !frag || !program) return null;
  gl.attachShader(program, vert);
  gl.attachShader(program, frag);
  gl.linkProgram(program);
  gl.deleteShader(vert);
  gl.deleteShader(frag);
  if (gl.getProgramParameter(program, gl.LINK_STATUS)) return program;
  gl.deleteProgram(program);
  return null;
}

// Returns null when WebGL2 is unavailable. One draw call per frame: gl.LINES over every segment.
export function createRenderer(
  canvas: HTMLCanvasElement,
  positions: Float32Array,
  edges: Uint32Array,
  ranks: Float32Array[],
  onLost: () => void,
): Renderer | null {
  const gl = canvas.getContext("webgl2", { antialias: true, alpha: true, premultipliedAlpha: true });
  if (!gl) return null;
  const program = link(gl);
  if (!program) return null;

  const aPos = gl.getAttribLocation(program, "aPos");
  const aRank = gl.getAttribLocation(program, "aRank");
  const aGhost = gl.getAttribLocation(program, "aGhost");
  const uClock = gl.getUniformLocation(program, "uClock");
  const uNever = gl.getUniformLocation(program, "uNever");
  const uUnlit = gl.getUniformLocation(program, "uUnlit");
  const uGhostAlpha = gl.getUniformLocation(program, "uGhostAlpha");
  let unlitAlpha = 0.16;
  let ghostAlpha = 0.42;

  // Positions are expanded once, so the two ends of segment k sit at line vertices 2k and 2k + 1.
  const verts = new Float32Array(edges.length * 2);
  for (let i = 0; i < edges.length; i++) {
    verts[2 * i] = positions[2 * edges[i]];
    verts[2 * i + 1] = positions[2 * edges[i] + 1];
  }
  const posBuffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, posBuffer);
  gl.bufferData(gl.ARRAY_BUFFER, verts, gl.STATIC_DRAW);
  const rankBuffers = ranks.map((r) => {
    const b = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, b);
    gl.bufferData(gl.ARRAY_BUFFER, r, gl.STATIC_DRAW);
    return b;
  });

  const vao = gl.createVertexArray();
  gl.bindVertexArray(vao);
  gl.bindBuffer(gl.ARRAY_BUFFER, posBuffer);
  gl.enableVertexAttribArray(aPos);
  gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 0, 0);
  gl.enableVertexAttribArray(aRank);

  gl.enable(gl.BLEND);
  gl.blendFunc(gl.ONE, gl.ONE_MINUS_SRC_ALPHA);
  gl.clearColor(0, 0, 0, 0);

  const handleLost = (event: Event) => {
    event.preventDefault();
    onLost();
  };
  canvas.addEventListener("webglcontextlost", handleLost);

  return {
    resize() {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      const w = Math.max(1, Math.round(canvas.clientWidth * dpr));
      const h = Math.max(1, Math.round(canvas.clientHeight * dpr));
      if (canvas.width !== w || canvas.height !== h) {
        canvas.width = w;
        canvas.height = h;
      }
      gl.viewport(0, 0, w, h);
    },
    setDim(unlit, ghost) {
      unlitAlpha = unlit;
      ghostAlpha = ghost;
    },
    draw(clock, method, ghost) {
      gl.clear(gl.COLOR_BUFFER_BIT);
      gl.useProgram(program);
      gl.bindVertexArray(vao);
      gl.uniform1f(uClock, clock);
      gl.uniform1f(uNever, NEVER / 10);
      gl.uniform1f(uUnlit, unlitAlpha);
      gl.uniform1f(uGhostAlpha, ghostAlpha);
      gl.bindBuffer(gl.ARRAY_BUFFER, rankBuffers[method]);
      gl.vertexAttribPointer(aRank, 1, gl.FLOAT, false, 0, 0);
      if (ghost >= 0) {
        gl.bindBuffer(gl.ARRAY_BUFFER, rankBuffers[ghost]);
        gl.enableVertexAttribArray(aGhost);
        gl.vertexAttribPointer(aGhost, 1, gl.FLOAT, false, 0, 0);
      } else {
        gl.disableVertexAttribArray(aGhost);
        gl.vertexAttrib1f(aGhost, NEVER);
      }
      gl.drawArrays(gl.LINES, 0, edges.length);
    },
    dispose() {
      canvas.removeEventListener("webglcontextlost", handleLost);
      gl.deleteVertexArray(vao);
      gl.deleteBuffer(posBuffer);
      rankBuffers.forEach((b) => gl.deleteBuffer(b));
      gl.deleteProgram(program);
      // The context itself is left to the garbage collector: losing it here would break a remount on the same canvas.
    },
  };
}
