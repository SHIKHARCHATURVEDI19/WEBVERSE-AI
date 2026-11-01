"use client";

import { Canvas, useFrame } from "@react-three/fiber";
import { useRef } from "react";
import * as THREE from "three";

function Sculpture() {
  const group = useRef<THREE.Group>(null);
  useFrame((state, delta) => {
    if (!group.current) return;
    group.current.rotation.y += delta * 0.22;
    group.current.rotation.x = Math.sin(state.clock.elapsedTime * 0.35) * 0.12;
    group.current.position.y = Math.sin(state.clock.elapsedTime * 0.7) * 0.08;
  });

  return (
    <group ref={group}>
      <mesh>
        <torusKnotGeometry args={[0.8, 0.24, 180, 24, 2, 3]} />
        <meshStandardMaterial color="#d66b35" roughness={0.28} metalness={0.48} />
      </mesh>
      <mesh position={[0.05, 0, 0]} scale={0.36}>
        <sphereGeometry args={[1, 48, 48]} />
        <meshStandardMaterial color="#f5d8b6" roughness={0.22} metalness={0.18} />
      </mesh>
    </group>
  );
}

export function ThreeHero() {
  return (
    <div className="three-hero-canvas" role="img" aria-label="Abstract 3D sculpture">
      <Canvas camera={{ position: [0, 0, 4.2], fov: 42 }} dpr={[1, 1.5]}>
        <ambientLight intensity={1.3} />
        <directionalLight position={[3, 4, 5]} intensity={2.2} />
        <pointLight position={[-3, -2, 2]} color="#f3a16d" intensity={1.5} />
        <Sculpture />
      </Canvas>
    </div>
  );
}
