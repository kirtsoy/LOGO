const fs = require('fs');
const path = require('path');

// Load Three.js in Node
const THREE = require(path.join(__dirname, 'assets', 'vendor', 'three.min.js'));
// Attach to global for BufferGeometryUtils
global.THREE = THREE;
require(path.join(__dirname, 'assets', 'vendor', 'BufferGeometryUtils.js'));

// Load custom font with Printed K
const fontJson = JSON.parse(fs.readFileSync(path.join(__dirname, 'assets', 'UnifrakturCook_PrintedK.json'), 'utf8'));
const font = new THREE.Font(fontJson);

const textVal = 'kirtsoy';
const size = 38;
const depth = 18;
const bevel = 3.2;
const bevelSegs = 8;
const overlapRatio = 0.15; // 15% overlap: all letters touch and fuse!

const chars = Array.from(textVal);
const scale = size / font.data.resolution;
const geometries = [];
let currentX = 0;
let tBounds = null;

const extrudeSettings = {
  steps: 1,
  depth: depth,
  bevelEnabled: true,
  bevelThickness: bevel,
  bevelSize: bevel * 0.75,
  bevelOffset: 0,
  bevelSegments: bevelSegs
};

for (let i = 0; i < chars.length; i++) {
  const char = chars[i];
  const glyph = font.data.glyphs[char] || font.data.glyphs['?'];
  if (!glyph) continue;

  const shapes = font.generateShapes(char, size);
  if (shapes && shapes.length > 0) {
    const charGeo = new THREE.ExtrudeGeometry(shapes, extrudeSettings);
    charGeo.translate(currentX, 0, 0);
    charGeo.computeBoundingBox();

    if (char.toLowerCase() === 't' && !tBounds) {
      const b = charGeo.boundingBox;
      tBounds = {
        minX: b.min.x,
        maxX: b.max.x,
        xCenter: (b.min.x + b.max.x) / 2,
        yBail: b.min.y + (b.max.y - b.min.y) * 0.84
      };
    }
    geometries.push(charGeo);
  }

  const advance = (glyph.ha !== undefined ? glyph.ha : 500) * scale;
  currentX += advance * (1.0 - overlapRatio);
}

const merged = THREE.BufferGeometryUtils.mergeBufferGeometries(geometries);
merged.computeBoundingBox();
const center = merged.boundingBox.getCenter(new THREE.Vector3());
merged.center();
merged.computeVertexNormals();

const holeCoords = {
  xCenter: tBounds.xCenter - center.x,
  xLeft: tBounds.minX - center.x,
  xRight: tBounds.maxX - center.x,
  yBail: tBounds.yBail - center.y,
  z: 0
};

console.log('Hole coordinates in centered mesh:', holeCoords);

// Export to OBJ
let objText = "# KIRTSOY Monolithic Interlocking Pendant with Printed K\n";
objText += "o Pendant_kirtsoy\n";
const pos = merged.attributes.position;
for (let i = 0; i < pos.count; i++) {
  objText += `v ${pos.getX(i).toFixed(4)} ${pos.getY(i).toFixed(4)} ${pos.getZ(i).toFixed(4)}\n`;
}
const norm = merged.attributes.normal;
if (norm) {
  for (let i = 0; i < norm.count; i++) {
    objText += `vn ${norm.getX(i).toFixed(4)} ${norm.getY(i).toFixed(4)} ${norm.getZ(i).toFixed(4)}\n`;
  }
}
if (merged.index) {
  const idx = merged.index;
  for (let f = 0; f < idx.count; f += 3) {
    const a = idx.getX(f) + 1;
    const b = idx.getX(f + 1) + 1;
    const c = idx.getX(f + 2) + 1;
    objText += `f ${a}//${a} ${b}//${b} ${c}//${c}\n`;
  }
} else {
  for (let f = 0; f < pos.count; f += 3) {
    const a = f + 1, b = f + 2, c = f + 3;
    objText += `f ${a}//${a} ${b}//${b} ${c}//${c}\n`;
  }
}

const tempObjPath = path.join(__dirname, 'temp_upright_interlocking.obj');
fs.writeFileSync(tempObjPath, objText, 'utf8');
console.log('Wrote upright interlocking OBJ to:', tempObjPath);

fs.writeFileSync(path.join(__dirname, 'hole_coords.json'), JSON.stringify(holeCoords, null, 2), 'utf8');
