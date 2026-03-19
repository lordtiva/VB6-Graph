import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
// @ts-ignore - WebGPU is new, types might be lagging or different
import WebGPU from 'three/addons/capabilities/WebGPU.js';
// @ts-ignore 
import { WebGPURenderer } from 'three/webgpu';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
// @ts-ignore - d3-force-3d allows 3D force simulation
import * as d3 from 'd3-force-3d';
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
  
  // LIVE SIMULATION STATE
  const simulationRef = useRef<any>(null);
  const simNodesRef = useRef<any[]>([]);
  const simLinksRef = useRef<any[]>([]);
  const instancedMeshRef = useRef<THREE.InstancedMesh | null>(null);
  const edgeGeometryRef = useRef<THREE.BufferGeometry | null>(null);
  const edgePositionsRef = useRef<Float32Array | null>(null);
  const labelSpritesRef = useRef<Map<string, THREE.Sprite>>(new Map());
  const nodeMapRef = useRef<Map<string, number>>(new Map());
  
  // SHARED GEOMETRIES (Optimize memory)
  // Base radius 3 makes nodes easier to click (larger hit volume)
  const nodeGeometryRef = useRef(new THREE.SphereGeometry(4, 12, 12));

  useEffect(() => {
    nodeGeometryRef.current.computeBoundingSphere();
  }, []);

  const textureCacheRef = useRef<Map<string, THREE.CanvasTexture>>(new Map());

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
        if (dist > 15) return;

        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        const rect = containerRef.current.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        raycaster.setFromCamera(mouse, cameraRef.current);
        
        let intersects: any[] = [];
        if (instancedMeshRef.current) {
          intersects = raycaster.intersectObject(instancedMeshRef.current, false);
        } else {
          intersects = raycaster.intersectObjects(nodesGroupRef.current.children, true);
        }
        
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

        // HOVER CURSOR CHANGE
        const onMouseMove = (e: MouseEvent) => {
          if (!containerRef.current || !cameraRef.current || !nodesGroupRef.current) return;
          const raycaster = new THREE.Raycaster();
          const mouse = new THREE.Vector2();
          const rect = containerRef.current.getBoundingClientRect();
          mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
          mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;
          raycaster.setFromCamera(mouse, cameraRef.current);
          
          let intersects: any[] = [];
          if (instancedMeshRef.current) {
            intersects = raycaster.intersectObject(instancedMeshRef.current, false);
          } else {
            intersects = raycaster.intersectObjects(nodesGroupRef.current.children, true);
          }
          containerRef.current.style.cursor = intersects.length > 0 ? 'pointer' : 'auto';
        };
        containerRef.current.addEventListener('mousemove', onMouseMove);

        // CLEANUP MOUSEMOVE
        const originalCleanup = (containerRef.current as any)._cleanup;
        (containerRef.current as any)._cleanup = () => {
          originalCleanup();
          containerRef.current?.removeEventListener('mousemove', onMouseMove);
        };
      }

      // ANIMATION LOOP
      const animate = () => {
        if (!isMounted || !rendererRef.current) return;
        requestAnimationFrame(animate);
        controls.update();
        
        // 1. UPDATE LIVE SIMULATION
        if (simulationRef.current) {
          // No need to call simulation.tick() as it runs in background by default, 
          // but we can if we want to synchronize it. d3-force starts ticking automatically.
          
          // 2. UPDATE NODE MESHES
          if (instancedMeshRef.current && simNodesRef.current.length > 0) {
            const mesh = instancedMeshRef.current;
            const dummy = new THREE.Object3D();
            
            simNodesRef.current.forEach((node, i) => {
              const isFocus = focusedNodeId === node.id;
              // Adjusted scale for new base radius 4 (original was scale 1.0, so we use 1/4 of that ratio)
              const s = Math.max(1.5, (node.size || 5) * (isFocus ? 6 : 1.1) / 4);
              dummy.scale.set(s, s, s);
              dummy.position.set(node.x, node.y, node.z);
              dummy.updateMatrix();
              mesh.setMatrixAt(i, dummy.matrix);
            });
            mesh.instanceMatrix.needsUpdate = true;
          }

          // 3. UPDATE EDGES
          if (edgeGeometryRef.current && edgePositionsRef.current && simLinksRef.current.length > 0) {
            const positions = edgePositionsRef.current;
            simLinksRef.current.forEach((link, i) => {
              const source = link.source;
              const target = link.target;
              const idx = i * 6;
              positions[idx] = source.x; positions[idx+1] = source.y; positions[idx+2] = source.z;
              positions[idx+3] = target.x; positions[idx+4] = target.y; positions[idx+5] = target.z;
            });
            edgeGeometryRef.current.getAttribute('position').needsUpdate = true;
          }

          // 4. UPDATE LABELS
          if (labelsGroupRef.current && labelSpritesRef.current.size > 0) {
            labelSpritesRef.current.forEach((sprite, nodeId) => {
              const node = simNodesRef.current.find(n => n.id === nodeId);
              if (node) {
                const isFocus = focusedNodeId === nodeId;
                const s = Math.max(6, (node.size || 5) * (isFocus ? 6 : 1.1));
                sprite.position.set(node.x, node.y + s + (isFocus ? 35 : 15), node.z);
              }
            });
          }
        } else {
           // Fallback soft rotation if no simulation
           if (nodesGroupRef.current) nodesGroupRef.current.rotation.y += 0.0003;
           if (edgesGroupRef.current) edgesGroupRef.current.rotation.y += 0.0003;
           if (labelsGroupRef.current) labelsGroupRef.current.rotation.y += 0.0003;
        }

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
        
        // Dispose of cached textures
        textureCacheRef.current.forEach(t => t.dispose());
        textureCacheRef.current.clear();
        
        if (simulationRef.current) {
          simulationRef.current.stop();
          simulationRef.current = null;
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

  // CONTENT EFFECT: Re-build Graph Meshes (Runs on Data change)
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
            // Note: We DON'T dispose m.map here because textures are cached
            m.dispose();
          });
        } else {
          // Note: We DON'T dispose obj.material.map here because textures are cached
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
    labelSpritesRef.current.clear();

    if (simulationRef.current) {
        simulationRef.current.stop();
    }

    console.log("[Graph3D] Rebuilding structure (Data/HiddenTypes changed)");

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
      
      // Adjusted scale for base radius 4
      const s = Math.max(1.5, (size || 5) * 1.1 / 4);
      dummy.scale.set(s, s, s);
      dummy.position.set(x || 0, y || 0, z || 0);
      dummy.updateMatrix();
      instancedMesh.setMatrixAt(i, dummy.matrix);

      // Initial Color (Standard Type Color)
      let color = new THREE.Color(TYPE_COLORS[type] || TYPE_COLORS.Unknown);
      instancedMesh.setColorAt(i, color);
      
      nodeMap.set(node.key, i);
      instanceToNodeId.set(i, node.key);
    });
    nodeMapRef.current = nodeMap;

    instancedMesh.instanceMatrix.needsUpdate = true;
    if (instancedMesh.instanceColor) instancedMesh.instanceColor.needsUpdate = true;
    
    // Store metadata for raycasting
    (instancedMesh as any)._instanceToNodeId = instanceToNodeId;
    nodesGroup.add(instancedMesh);
    instancedMeshRef.current = instancedMesh;

    // PREPARE SIMULATION DATA
    const nodesForSim = visibleNodes.map(n => ({
        id: n.key,
        x: n.attributes.x || 0,
        y: n.attributes.y || 0,
        z: n.attributes.z || 0,
        size: n.attributes.size || 5
    }));
    simNodesRef.current = nodesForSim;

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

        let colorObj = new THREE.Color(0x30363d);
        colorObj.multiplyScalar(0.4); // Subtle default edges

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
      
      edgeGeometryRef.current = edgeGeometry;
      edgePositionsRef.current = positions;

      // PREPARE LINKS FOR SIM
      const linksForSim = visibleEdges.map(e => ({
          source: nodesForSim.findIndex(n => n.id === e.source),
          target: nodesForSim.findIndex(n => n.id === e.target)
      })).filter(l => l.source !== -1 && l.target !== -1);
      simLinksRef.current = linksForSim;
    }

    // (Labels moved to separate selection effect for performance)

    // 5. START SIMULATION
    const simulation = d3.forceSimulation(nodesForSim, 3)
      .force("link", d3.forceLink(simLinksRef.current).distance(120).strength(0.8))
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(0, 0, 0))
      .force("x", d3.forceX().strength(0.05))
      .force("y", d3.forceY().strength(0.05))
      .force("z", d3.forceZ().strength(0.05));

    simulationRef.current = simulation;

    // 6. ZOOM TO FIT (If data changed or first time)
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

  }, [isInitialized, data, hiddenTypes, onNodeClick]);

  // SELECTION EFFECT: Update colors and labels (VERY FAST)
  useEffect(() => {
    if (!isInitialized || !instancedMeshRef.current || !labelsGroupRef.current) return;
    
    const mesh = instancedMeshRef.current;
    const labelsGroup = labelsGroupRef.current;
    const edgeGeometry = edgeGeometryRef.current;
    
    // 1. UPDATE NODE COLORS
    data.nodes.forEach((node) => {
        const idx = nodeMapRef.current.get(node.key);
        if (idx === undefined) return;

        let color = new THREE.Color(TYPE_COLORS[node.attributes.type] || TYPE_COLORS.Unknown);
        if (focusedNodeId) {
            const isFocus = node.key === focusedNodeId;
            const isNeighbor = data.edges.some(e => 
                (e.source === focusedNodeId && e.target === node.key) || 
                (e.target === focusedNodeId && e.source === node.key)
            );
            
            if (isFocus) color = new THREE.Color(0x00faff);
            else if (isNeighbor) color = color.clone().multiplyScalar(1.5);
            else color = color.clone().multiplyScalar(0.1);
        }
        mesh.setColorAt(idx, color);
    });
    if (mesh.instanceColor) mesh.instanceColor.needsUpdate = true;

    // 2. UPDATE EDGE COLORS
    if (edgeGeometry) {
        const colors = edgeGeometry.getAttribute('color') as THREE.BufferAttribute;
        const visibleEdges = data.edges.filter(edge => {
            const source = data.nodes.find(n => n.key === edge.source);
            const target = data.nodes.find(n => n.key === edge.target);
            return source && target && !hiddenTypes.has(source.attributes.type) && !hiddenTypes.has(target.attributes.type);
        });

        visibleEdges.forEach((edge, i) => {
            const idx = i * 6;
            const isRelated = focusedNodeId === edge.source || focusedNodeId === edge.target;
            let colorObj = new THREE.Color(isRelated ? (edge.source === focusedNodeId ? 0x58a6ff : 0xffa657) : 0x30363d);
            
            if (focusedNodeId && !isRelated) {
                colorObj.multiplyScalar(0.05);
            } else if (!focusedNodeId) {
                colorObj.multiplyScalar(0.4);
            }
            
            colors.setXYZ(i * 2, colorObj.r, colorObj.g, colorObj.b);
            colors.setXYZ(i * 2 + 1, colorObj.r, colorObj.g, colorObj.b);
        });
        colors.needsUpdate = true;
    }

    // 3. UPDATE LABELS (Re-build only needed labels)
    const clearGroup = (group: THREE.Group) => {
        while(group.children.length > 0) {
          const child = group.children[0];
          if ((child as any).material) {
              if (Array.isArray((child as any).material)) (child as any).material.forEach((m: any) => m.dispose());
              else (child as any).material.dispose();
          }
          group.remove(child);
        }
    };
    clearGroup(labelsGroup);
    labelSpritesRef.current.clear();

    if (focusedNodeId) {
        const neighborNodes = data.edges
          .filter(e => e.source === focusedNodeId || e.target === focusedNodeId)
          .map(e => e.source === focusedNodeId ? e.target : e.source)
          .map(id => data.nodes.find(n => n.key === id))
          .filter(n => n && !hiddenTypes.has(n.attributes.type)) as any[];

        const topNeighbors = neighborNodes
          .sort((a, b) => (b.attributes.size || 0) - (a.attributes.size || 0))
          .slice(0, 20);

        const nodesToLabel = [
          data.nodes.find(n => n.key === focusedNodeId),
          ...topNeighbors
        ].filter(n => n !== undefined) as any[];

        nodesToLabel.forEach(node => {
          const isFocus = focusedNodeId === node.key;
          const cacheKey = `${node.key}-${isFocus ? 'focus' : 'neighbor'}`;
          let texture = textureCacheRef.current.get(cacheKey);
          
          if (!texture) {
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            if (context) {
              canvas.width = 512; canvas.height = 128;
              context.font = `Bold ${isFocus ? '48px' : '38px'} Inter, Arial`;
              context.fillStyle = isFocus ? '#00faff' : '#c9d1d9';
              context.textAlign = 'center';
              context.fillText(node.attributes.label || node.key, 256, 100);
              texture = new THREE.CanvasTexture(canvas);
              textureCacheRef.current.set(cacheKey, texture);
            }
          }

          if (texture) {
            const spriteMaterial = new THREE.SpriteMaterial({ map: texture, transparent: true, opacity: isFocus ? 1.0 : 0.7 });
            const sprite = new THREE.Sprite(spriteMaterial);
            const sw = isFocus ? 180 : 90;
            const sh = isFocus ? 45 : 22.5;
            
            // Note: Position will be set in the animate loop based on sim data
            sprite.scale.set(sw, sh, 1);
            labelsGroup.add(sprite);
            labelSpritesRef.current.set(node.key, sprite);
          }
        });
    }

  }, [focusedNodeId, isInitialized]);

  return <div ref={containerRef} className="w-full h-full cursor-pointer" />;
};

export default GraphView3D;
