import React, { useRef, useMemo, useEffect } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

const PARTICLE_COUNT = 8000;

interface VisualEchoNodeProps {
  shape: 'sphere' | 'cube' | 'vortex' | 'cloud';
  color: string;
  energy: number;
}

const VisualEchoNode: React.FC<VisualEchoNodeProps> = ({ shape, color, energy }) => {
  const meshRef = useRef<THREE.Points>(null);
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  const [positions, targetPositions] = useMemo(() => {
    const pos = new Float32Array(PARTICLE_COUNT * 3);
    const target = new Float32Array(PARTICLE_COUNT * 3);

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      // Start in a random sphere/nebula
      const r = 2 * Math.pow(Math.random(), 1/3);
      const theta = Math.random() * 2 * Math.PI;
      const phi = Math.acos(2 * Math.random() - 1);

      pos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      pos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i * 3 + 2] = r * Math.cos(phi);

      target[i * 3] = pos[i * 3];
      target[i * 3 + 1] = pos[i * 3 + 1];
      target[i * 3 + 2] = pos[i * 3 + 2];
    }
    return [pos, target];
  }, []);

  useEffect(() => {
    if (!meshRef.current) return;
    const target = meshRef.current.geometry.attributes.targetPosition.array as Float32Array;

    for (let i = 0; i < PARTICLE_COUNT; i++) {
      if (shape === 'sphere') {
        const r = 1.5;
        const theta = Math.random() * 2 * Math.PI;
        const phi = Math.acos(2 * Math.random() - 1);
        target[i * 3] = r * Math.sin(phi) * Math.cos(theta);
        target[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
        target[i * 3 + 2] = r * Math.cos(phi);
      } else if (shape === 'cube') {
        target[i * 3] = (Math.random() - 0.5) * 2.5;
        target[i * 3 + 1] = (Math.random() - 0.5) * 2.5;
        target[i * 3 + 2] = (Math.random() - 0.5) * 2.5;
      } else if (shape === 'vortex') {
        const angle = i * 0.1;
        const r = i * 0.0003;
        target[i * 3] = r * Math.cos(angle);
        target[i * 3 + 1] = (i / PARTICLE_COUNT - 0.5) * 3;
        target[i * 3 + 2] = r * Math.sin(angle);
      } else {
        // Cloud/Nebula
        target[i * 3] = (Math.random() - 0.5) * 4;
        target[i * 3 + 1] = (Math.random() - 0.5) * 4;
        target[i * 3 + 2] = (Math.random() - 0.5) * 4;
      }
    }
    meshRef.current.geometry.attributes.targetPosition.needsUpdate = true;

    if (materialRef.current) {
        materialRef.current.uniforms.uMorphStart.value = 0.0;
        // Reset morph progress
        materialRef.current.uniforms.uMorph.value = 0.0;
    }
  }, [shape]);

  const uniforms = useMemo(() => ({
    uTime: { value: 0 },
    uMorph: { value: 0 },
    uMorphStart: { value: 0 },
    uColor: { value: new THREE.Color(color) },
    uEnergy: { value: energy }
  }), []);

  useEffect(() => {
    if (materialRef.current) {
      materialRef.current.uniforms.uColor.value.set(color);
      materialRef.current.uniforms.uEnergy.value = energy;
    }
  }, [color, energy]);

  useFrame((state) => {
    if (materialRef.current) {
      materialRef.current.uniforms.uTime.value = state.clock.getElapsedTime();
      // Smooth morphing
      materialRef.current.uniforms.uMorph.value = THREE.MathUtils.lerp(
        materialRef.current.uniforms.uMorph.value,
        1.0,
        0.05
      );
    }
    if (meshRef.current) {
        meshRef.current.rotation.y += 0.002 + (energy * 0.01);
    }
  });

  return (
    <points ref={meshRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
        <bufferAttribute
          attach="attributes-targetPosition"
          args={[targetPositions, 3]}
        />
      </bufferGeometry>
      <shaderMaterial
        ref={materialRef}
        uniforms={uniforms}
        vertexShader={`
          uniform float uTime;
          uniform float uMorph;
          uniform float uEnergy;
          attribute vec3 targetPosition;
          varying float vAlpha;

          void main() {
            vec3 pos = mix(position, targetPosition, uMorph);

            // Energy vibration
            pos.x += sin(uTime * 5.0 + position.z) * 0.05 * uEnergy;
            pos.y += cos(uTime * 5.0 + position.x) * 0.05 * uEnergy;

            vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
            gl_PointSize = (25.0 / -mvPosition.z) * (0.8 + uEnergy * 1.5);
            gl_Position = projectionMatrix * mvPosition;
            vAlpha = 1.0 / (1.0 + length(pos) * 0.1);
          }
        `}
        fragmentShader={`
          uniform vec3 uColor;
          varying float vAlpha;
          void main() {
            float d = distance(gl_PointCoord, vec2(0.5));
            if (d > 0.5) discard;
            float strength = 1.0 - (d * 2.0);
            gl_FragColor = vec4(uColor, strength * vAlpha);
          }
        `}
        transparent
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </points>
  );
};

export default VisualEchoNode;
