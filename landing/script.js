/* =========================================================
   THREE.JS SCENE SETUP
   Creates the cinematic animated background grid
========================================================= */

// Create scene and camera
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(
  60,
  innerWidth / innerHeight,
  0.1,
  1000
);

// Position camera slightly above looking down
camera.position.set(0, 3, 12);

// WebGL renderer
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
document.body.appendChild(renderer.domElement);



/* =========================================================
   FAKE TELEMETRY ANIMATION (HUD numbers moving)
   Later you can replace this with real API values
========================================================= */

const speedEl = document.querySelector(".left .value");
const throttleEl = document.querySelectorAll(".left .value")[1];
const brakeEl = document.querySelectorAll(".right .value")[0];
const gearEl = document.querySelectorAll(".right .value")[1];

let speed = 200;
let throttle = 40;
let brake = 0;
let gear = 4;

function updateTelemetry() {
  // Random realistic variation
  speed += Math.random() * 8 - 4;
  throttle += Math.random() * 10 - 5;
  brake = Math.random() > 0.85 ? Math.random() * 40 : 0;

  // Gear derived from speed
  gear = Math.min(8, Math.max(1, Math.floor(speed / 40)));

  // Clamp values to realistic ranges
  speed = Math.max(120, Math.min(340, speed));
  throttle = Math.max(0, Math.min(100, throttle));

  // Update HUD
  speedEl.innerHTML = `${Math.floor(speed)} <span>KM/H</span>`;
  throttleEl.innerHTML = `${Math.floor(throttle)} <span>%</span>`;
  brakeEl.innerHTML = `${Math.floor(brake)} <span>%</span>`;
  gearEl.innerHTML = gear;
}

// Update every 120ms
setInterval(updateTelemetry, 120);



/* =========================================================
   SHADERS — FUTURISTIC TELEMETRY GRID FLOOR
========================================================= */

const vertexShader = `
varying vec2 vUv;
void main() {
  vUv = uv;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
}
`;

const fragmentShader = `
uniform float uTime;
uniform float uScan;
varying vec2 vUv;

// Grid generator
float grid(vec2 uv, float s){
  vec2 g = abs(fract(uv*s-0.5)-0.5)/fwidth(uv*s);
  return 1.0 - min(min(g.x,g.y),1.0);
}

void main(){
  vec2 uv = vUv;

  // Perspective illusion
  float perspective = 1.0/(1.0+uv.y*2.0);
  vec2 guv = vec2(uv.x*perspective, uv.y);

  // Two grid layers
  float g1 = grid(guv, 20.0)*0.4;
  float g2 = grid(guv, 80.0)*0.15;

  // Scanning beam
  float scan = exp(-abs(uv.x-uScan)*20.0)*0.8;

  vec3 cyan = vec3(0.0,0.9,1.0);
  vec3 color = cyan*(g1+g2) + cyan*scan;

  gl_FragColor = vec4(color,1.0);
}
`;


/* =========================================================
   GRID PLANE MESH (the animated floor)
========================================================= */

const plane = new THREE.Mesh(
  new THREE.PlaneGeometry(100, 50),
  new THREE.ShaderMaterial({
    uniforms: {
      uTime: { value: 0 },
      uScan: { value: 0 }
    },
    vertexShader,
    fragmentShader
  })
);

// Tilt the grid for cinematic perspective
plane.rotation.x = -Math.PI / 2.4;
plane.position.y = -2;
plane.position.z = -10;

scene.add(plane);



/* =========================================================
   ANIMATION LOOP
========================================================= */

function animate(t) {
  requestAnimationFrame(animate);

  // Animate shader uniforms
  plane.material.uniforms.uTime.value = t * 0.001;
  plane.material.uniforms.uScan.value = (t * 0.0002) % 1;

  // Slight camera drift for life
  camera.position.x = Math.sin(t * 0.0003) * 2;
  camera.lookAt(0, 0, 0);

  renderer.render(scene, camera);
}

animate();



/* =========================================================
   RESPONSIVE RESIZE
========================================================= */

window.onresize = () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
};



/* =========================================================
   CONNECT TO LAPVIS STREAMLIT DASHBOARD
========================================================= */

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("enterBtn");

  btn.addEventListener("click", () => {
    btn.innerText = "Loading Telemetry...";

    setTimeout(() => {
      window.location.href = "http://localhost:8501";
    }, 1200);
  });
});