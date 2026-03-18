import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
// @ts-ignore - WebGPU is new, types might be lagging or different
import WebGPU from 'three/addons/capabilities/WebGPU.js';
// @ts-ignore 
import { WebGPURenderer } from 'three/webgpu';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { GraphData } from '../types';
import { TYPE_COLORS } from './GraphView';

interface GraphView3DProps {
  data: GraphData;
  onNodeClick: (nodeId: string) => void;
  hiddenTypes: Set<string>;
  focusedNodeId?: string | null;
  communityView?: boolean;
}

const GraphView3D: React.FC<GraphView3DProps> = ({ 
  data, 
  onNodeClick, 
  hiddenTypes, 
  focusedNodeId, 
  communityView = false 
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const rendererRef = useRef<any>(null);
  const sceneRef = useRef<THREE.Scene | null>(null);
  const cameraRef = useRef<THREE.PerspectiveCamera | null>(null);
  const nodesGroupRef = useRef<THREE.Group | null>(null);
  const edgesGroupRef = useRef<THREE.Group | null>(null);
  const labelsGroupRef = useRef<THREE.Group | null>(null);
  const controlsRef = useRef<any>(null);

  const readyRef = useRef(false);
  const lastDataKeyRef = useRef<string>("");
  const [isInitialized, setIsInitialized] = useState(false);
  
  // SHARED GEOMETRIES (Optimize memory)
  const nodeGeometryRef = useRef(new THREE.SphereGeometry(1, 12, 12));

  // INFRASTRUCTURE EFFECT: Setup Scene, Camera, Renderer (Runs once)
  useEffect(() => {
    if (!containerRef.current) return;
    let isMounted = true;

    // Infrastructure setup
    const setupInfrastructure = async () => {
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x0d1117);
      sceneRef.current = scene;

      const camera = new THREE.PerspectiveCamera(
        60, 
        containerRef.current!.clientWidth / containerRef.current!.clientHeight, 
        1, 
        40000
      );
      camera.position.z = 5000;
      cameraRef.current = camera;

      // RENDERER SETUP
      let renderer: any;
      try {
        // @ts-ignore
        if (typeof WebGPURenderer !== 'undefined' && WebGPU.isAvailable()) {
          renderer = new WebGPURenderer({ antialias: true });
          await renderer.init();
        } else {
          throw new Error("WebGPU not available");
        }
      } catch (e) {
        renderer = new THREE.WebGLRenderer({ antialias: true });
      }
      
      if (!isMounted) {
        renderer.dispose();
        return;
      }

      renderer.setPixelRatio(window.devicePixelRatio);
      renderer.setSize(containerRef.current!.clientWidth, containerRef.current!.clientHeight);
      containerRef.current!.appendChild(renderer.domElement);
      rendererRef.current = renderer;

      const controls = new OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controlsRef.current = controls;

      // PERMANENT GROUPS
      const nodesGroup = new THREE.Group();
      const edgesGroup = new THREE.Group();
      const labelsGroup = new THREE.Group();
      scene.add(nodesGroup);
      scene.add(edgesGroup);
      scene.add(labelsGroup);
      nodesGroupRef.current = nodesGroup;
      edgesGroupRef.current = edgesGroup;
      labelsGroupRef.current = labelsGroup;

      // PERMANENT LIGHTS
      const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
      scene.add(ambientLight);
      const pointLight = new THREE.PointLight(0xffffff, 1.2);
      camera.add(pointLight);
      scene.add(camera);

      // MOUSE INTERACTION
      let mouseDownPos = { x: 0, y: 0 };
      const onMouseDown = (e: MouseEvent) => { mouseDownPos = { x: e.clientX, y: e.clientY }; };
      const onMouseUp = (e: MouseEvent) => {
        if (!containerRef.current || !cameraRef.current || !nodesGroupRef.current) return;
        const dist = Math.sqrt(Math.pow(e.clientX - mouseDownPos.x, 2) + Math.pow(e.clientY - mouseDownPos.y, 2));
        if (dist > 5) return;

        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        const rect = containerRef.current.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        raycaster.setFromCamera(mouse, cameraRef.current);
        const intersects = raycaster.intersectObjects(nodesGroupRef.current.children);
        
        if (intersects.length > 0) {
          const intersect = intersects[0];
          // Support for InstancedMesh
          if (intersect.instanceId !== undefined && (intersect.object as any)._instanceToNodeId) {
            const nodeId = (intersect.object as any)._instanceToNodeId.get(intersect.instanceId);
            if (nodeId) onNodeClick(nodeId);
          } else if (intersect.object.userData.id) {
            onNodeClick(intersect.object.userData.id);
          }
        } else {
          // @ts-ignore
          onNodeClick(null);
        }
      };

      if (containerRef.current) {
        containerRef.current.addEventListener('mousedown', onMouseDown);
        containerRef.current.addEventListener('mouseup', onMouseUp);
      }

      // ANIMATION LOOP
      const animate = () => {
        if (!isMounted || !rendererRef.current) return;
        requestAnimationFrame(animate);
        controls.update();
        if (nodesGroupRef.current) nodesGroupRef.current.rotation.y += 0.0003;
        if (edgesGroupRef.current) edgesGroupRef.current.rotation.y += 0.0003;
        if (labelsGroupRef.current) labelsGroupRef.current.rotation.y += 0.0003;
        rendererRef.current.render(scene, camera);
      };
      animate();

      const handleResize = () => {
        if (!containerRef.current || !rendererRef.current || !cameraRef.current) return;
        cameraRef.current.aspect = containerRef.current.clientWidth / containerRef.current.clientHeight;
        cameraRef.current.updateProjectionMatrix();
        rendererRef.current.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
      };
      window.addEventListener('resize', handleResize);

      // STORE CLEANUP DATA
      (containerRef.current as any)._cleanup = () => {
        window.removeEventListener('resize', handleResize);
        containerRef.current?.removeEventListener('mousedown', onMouseDown);
        containerRef.current?.removeEventListener('mouseup', onMouseUp);
        if (rendererRef.current?.domElement && containerRef.current?.contains(rendererRef.current.domElement)) {
          containerRef.current.removeChild(rendererRef.current.domElement);
        }
        renderer.dispose();
      };

      readyRef.current = true;
      setIsInitialized(true);
    };

    setupInfrastructure();

    return () => {
      isMounted = false;
      const cleanup = (containerRef.current as any)?._cleanup;
      if (cleanup) cleanup();
    };
  }, []); // Only once

  // CONTENT EFFECT: Re-build Graph Meshes (Runs on Selection/Data change)
  useEffect(() => {
    if (!isInitialized || !nodesGroupRef.current || !edgesGroupRef.current || !labelsGroupRef.current) return;

    const nodesGroup = nodesGroupRef.current;
    const edgesGroup = edgesGroupRef.current;
    const labelsGroup = labelsGroupRef.current;

    // 1. CLEAR PREVIOUS MESHES (With proper disposal to avoid memory leaks)
    const disposeObject = (obj: any) => {
      if (obj.geometry) obj.geometry.dispose();
      if (obj.material) {
        if (Array.isArray(obj.material)) {
          obj.material.forEach((m: any) => {
            if (m.map) m.map.dispose();
            m.dispose();
          });
        } else {
          if (obj.material.map) obj.material.map.dispose();
          obj.material.dispose();
        }
      }
    };

    const clearGroup = (group: THREE.Group) => {
      while(group.children.length > 0) {
        const child = group.children[0];
        disposeObject(child);
        group.remove(child);
      }
    };

    clearGroup(nodesGroup);
    clearGroup(edgesGroup);
    clearGroup(labelsGroup);

    console.log("[Graph3D] Updating meshes (Optimized), focused:", focusedNodeId);

    const visibleNodes = data.nodes.filter(n => !hiddenTypes.has(n.attributes.type));
    if (visibleNodes.length === 0) return;

    // 2. CREATE INSTANCED NODES
    const nodeGeo = nodeGeometryRef.current;
    const nodeMat = new THREE.MeshPhongMaterial({ 
      shininess: 100,
      emissive: 0x000000,
      emissiveIntensity: 0
    });
    
    const instancedMesh = new THREE.InstancedMesh(nodeGeo, nodeMat, visibleNodes.length);
    instancedMesh.instanceMatrix.setUsage(THREE.StaticDrawUsage);
    
    const dummy = new THREE.Object3D();
    const nodeMap = new Map<string, number>(); // nodeKey -> instanceId
    const instanceToNodeId = new Map<number, string>(); // instanceId -> nodeKey

    visibleNodes.forEach((node, i) => {
      const { size, x, y, z, type } = node.attributes;
      const isFocus = focusedNodeId === node.key;
      
      const s = Math.max(6, (size || 5) * (isFocus ? 6 : 1.1));
      dummy.scale.set(s, s, s);
      dummy.position.set(x || 0, y || 0, z || 0);
      dummy.updateMatrix();
      instancedMesh.setMatrixAt(i, dummy.matrix);

      // Color logic
      let color = new THREE.Color(TYPE_COLORS[type] || TYPE_COLORS.Unknown);
      if (focusedNodeId) {
        const isNeighbor = data.edges.some(e => 
          (e.source === focusedNodeId && e.target === node.key) || 
          (e.target === focusedNodeId && e.source === node.key)
        );
        if (isFocus) color = new THREE.Color(0x00faff);
        else if (isNeighbor) color = color.clone().multiplyScalar(1.5);
        else color = color.clone().multiplyScalar(0.1);
      }
      instancedMesh.setColorAt(i, color);
      
      nodeMap.set(node.key, i);
      instanceToNodeId.set(i, node.key);
    });

    instancedMesh.instanceMatrix.needsUpdate = true;
    if (instancedMesh.instanceColor) instancedMesh.instanceColor.needsUpdate = true;
    
    // Store metadata for raycasting
    (instancedMesh as any)._instanceToNodeId = instanceToNodeId;
    nodesGroup.add(instancedMesh);

    // 3. CREATE BATCHED EDGES (LineSegments)
    const visibleEdges = data.edges.filter(edge => {
      const source = data.nodes.find(n => n.key === edge.source);
      const target = data.nodes.find(n => n.key === edge.target);
      return source && target && !hiddenTypes.has(source.attributes.type) && !hiddenTypes.has(target.attributes.type);
    });

    if (visibleEdges.length > 0) {
      const edgeGeometry = new THREE.BufferGeometry();
      const positions = new Float32Array(visibleEdges.length * 6);
      const colors = new Float32Array(visibleEdges.length * 6);

      visibleEdges.forEach((edge, i) => {
        const source = data.nodes.find(n => n.key === edge.source)!;
        const target = data.nodes.find(n => n.key === edge.target)!;
        
        const idx = i * 6;
        positions[idx] = source.attributes.x || 0;
        positions[idx+1] = source.attributes.y || 0;
        positions[idx+2] = source.attributes.z || 0;
        positions[idx+3] = target.attributes.x || 0;
        positions[idx+4] = target.attributes.y || 0;
        positions[idx+5] = target.attributes.z || 0;

        const isRelated = focusedNodeId === edge.source || focusedNodeId === edge.target;
        let colorObj = new THREE.Color(isRelated ? (edge.source === focusedNodeId ? 0x58a6ff : 0xffa657) : 0x30363d);
        
        // Handle opacity via color darkening if focused
        if (focusedNodeId && !isRelated) {
          colorObj.multiplyScalar(0.05); // Fade out unrelated edges
        } else if (!focusedNodeId) {
          colorObj.multiplyScalar(0.4); // Subtle default edges
        }

        colors[idx] = colorObj.r; colors[idx+1] = colorObj.g; colors[idx+2] = colorObj.b;
        colors[idx+3] = colorObj.r; colors[idx+4] = colorObj.g; colors[idx+5] = colorObj.b;
      });

      edgeGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      edgeGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
      
      const edgeMaterial = new THREE.LineBasicMaterial({ 
        vertexColors: true, 
        transparent: true, 
        opacity: 0.8 
      });
      edgesGroup.add(new THREE.LineSegments(edgeGeometry, edgeMaterial));
    }

    // 4. LABELS (Limit to focused + important neighbors)
    if (focusedNodeId) {
      visibleNodes.forEach(node => {
        const isFocus = focusedNodeId === node.key;
        const isNeighbor = data.edges.some(e => 
          (e.source === focusedNodeId && e.target === node.key) || 
          (e.target === focusedNodeId && e.source === node.key)
        );

        if (isFocus || isNeighbor) {
          if (isNeighbor && !isFocus) {
             const neighborCount = data.edges.filter(e => e.source === focusedNodeId || e.target === focusedNodeId).length;
             if (neighborCount > 30 && (node.attributes.size || 0) < 15) return;
          }

          const canvas = document.createElement('canvas');
          const context = canvas.getContext('2d');
          if (context) {
            canvas.width = 512; canvas.height = 128;
            context.font = `Bold ${isFocus ? '48px' : '38px'} Inter, Arial`;
            context.fillStyle = isFocus ? '#00faff' : '#c9d1d9';
            context.textAlign = 'center';
            context.fillText(node.attributes.label, 256, 100);
            
            const texture = new THREE.CanvasTexture(canvas);
            const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true, opacity: isFocus ? 1.0 : 0.7 });
            const sprite = new THREE.Sprite(spriteMaterial);
            
            const sw = isFocus ? 180 : 90;
            const sh = isFocus ? 45 : 22.5;
            const s = Math.max(6, (node.attributes.size || 5) * (isFocus ? 6 : 1.1));
            sprite.scale.set(sw, sh, 1);
            sprite.position.set(node.attributes.x || 0, (node.attributes.y || 0) + s + (isFocus ? 35 : 15), node.attributes.z || 0);
            labelsGroup.add(sprite);
          }
        }
      });
    }

    // 5. ZOOM TO FIT (If data changed or first time)
    const currentDataKey = `${data.nodes.length}-${data.edges.length}-${hiddenTypes.size}`;
    if (lastDataKeyRef.current !== currentDataKey && data.nodes.length > 0) {
      setTimeout(() => {
        if (!cameraRef.current || !controlsRef.current) return;
        const box = new THREE.Box3();
        visibleNodes.forEach(node => {
          box.expandByPoint(new THREE.Vector3(node.attributes.x || 0, node.attributes.y || 0, node.attributes.z || 0));
        });
        if (box.isEmpty()) return;

        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        const maxDim = Math.max(size.x, size.y, size.z);
        const fov = cameraRef.current.fov * (Math.PI / 180);
        let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2)) * 1.8;

        cameraRef.current.position.set(center.x, center.y, center.z + cameraZ);
        cameraRef.current.lookAt(center);
        controlsRef.current.target.set(center.x, center.y, center.z);
        controlsRef.current.update();
        lastDataKeyRef.current = currentDataKey;
      }, 100);
    }

  }, [isInitialized, data, hiddenTypes, focusedNodeId, onNodeClick]);

  return <div ref={containerRef} className="w-full h-full cursor-pointer" />;
};

export default GraphView3D;
