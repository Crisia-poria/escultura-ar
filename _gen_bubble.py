import struct, json, math

# Organic profile: (height_fraction 0=bottom to 1=top, radius_x, radius_z)
# Based on the aluminum sculpture silhouette — elliptical cross-section (x wider than z)
PROFILE = [
    (0.00, 0.018, 0.013),
    (0.03, 0.060, 0.045),
    (0.07, 0.105, 0.078),
    (0.13, 0.128, 0.095),
    (0.19, 0.118, 0.088),
    (0.25, 0.082, 0.060),
    (0.30, 0.100, 0.074),
    (0.36, 0.138, 0.102),
    (0.42, 0.148, 0.110),
    (0.47, 0.128, 0.094),
    (0.52, 0.086, 0.063),
    (0.57, 0.112, 0.082),
    (0.63, 0.146, 0.107),
    (0.68, 0.152, 0.112),
    (0.73, 0.132, 0.097),
    (0.77, 0.112, 0.082),
    (0.82, 0.138, 0.101),
    (0.87, 0.148, 0.108),
    (0.91, 0.120, 0.088),
    (0.95, 0.082, 0.060),
    (0.98, 0.048, 0.035),
    (1.00, 0.018, 0.013),
]

HEIGHT = 0.55   # meters
SLICES = 56     # circumference divisions
STACKS = 88     # vertical divisions (interpolated)

def interp_profile(t):
    for i in range(len(PROFILE) - 1):
        t0, rx0, rz0 = PROFILE[i]
        t1, rx1, rz1 = PROFILE[i + 1]
        if t0 <= t <= t1:
            f = (t - t0) / (t1 - t0) if t1 > t0 else 0.0
            return rx0 + f * (rx1 - rx0), rz0 + f * (rz1 - rz0)
    return PROFILE[-1][1], PROFILE[-1][2]

pos, nor, uvs, idx = [], [], [], []

for i in range(STACKS + 1):
    t = i / STACKS
    y = (t - 0.5) * HEIGHT
    rx, rz = interp_profile(t)

    eps = 0.005
    rx_u, rz_u = interp_profile(min(t + eps, 1.0))
    rx_d, rz_d = interp_profile(max(t - eps, 0.0))
    drx = (rx_u - rx_d) / (2 * eps * HEIGHT)
    drz = (rz_u - rz_d) / (2 * eps * HEIGHT)

    for j in range(SLICES + 1):
        angle = 2 * math.pi * j / SLICES
        ca, sa = math.cos(angle), math.sin(angle)

        x = rx * ca
        z = rz * sa

        # tangent along circumference
        tx1, ty1, tz1 = -rx * sa, 0.0, rz * ca
        # tangent along height axis
        tx2, ty2, tz2 = drx * ca, 1.0, drz * sa
        # cross product
        nx = ty1 * tz2 - tz1 * ty2
        ny = tz1 * tx2 - tx1 * tz2
        nz = tx1 * ty2 - ty1 * tx2
        nl = math.sqrt(nx*nx + ny*ny + nz*nz)
        if nl > 1e-8:
            nx, ny, nz = nx/nl, ny/nl, nz/nl
        else:
            nx, ny, nz = ca, 0.0, sa

        # Rotate -90° on X: new=(x, z, -y) → lies flat on XZ plane
        pos += [x, z, -y]
        nor += [nx, nz, -ny]
        uvs += [j / SLICES, t]

for i in range(STACKS):
    for j in range(SLICES):
        a = i * (SLICES + 1) + j
        b = a + SLICES + 1
        idx += [a, b, a+1, b, b+1, a+1]

# Animation: scale pulse 1.0 -> 1.06 -> 1.0 over 2 seconds (LINEAR, loops)
anim_times  = [0.0, 1.0, 2.0]
anim_scales = [1.0,1.0,1.0,  1.06,1.06,1.03,  1.0,1.0,1.0]

def pad4(data, pad_byte=b'\x00'):
    r = len(data) % 4
    return data + pad_byte * ((4 - r) % 4)

idx_bytes   = pad4(struct.pack(f'{len(idx)}H', *idx))
pos_bytes   = pad4(struct.pack(f'{len(pos)}f', *pos))
nor_bytes   = pad4(struct.pack(f'{len(nor)}f', *nor))
uv_bytes    = pad4(struct.pack(f'{len(uvs)}f', *uvs))
time_bytes  = pad4(struct.pack(f'{len(anim_times)}f', *anim_times))
scale_bytes = pad4(struct.pack(f'{len(anim_scales)}f', *anim_scales))

bin_data = idx_bytes + pos_bytes + nor_bytes + uv_bytes + time_bytes + scale_bytes

offsets = [0]
for b in [idx_bytes, pos_bytes, nor_bytes, uv_bytes, time_bytes]:
    offsets.append(offsets[-1] + len(b))

nv = len(pos) // 3
ni = len(idx)
mn = [min(pos[i::3]) for i in range(3)]
mx = [max(pos[i::3]) for i in range(3)]

gltf = {
  "asset": {"version": "2.0", "generator": "bubble-organic-v2"},
  "scene": 0,
  "scenes": [{"nodes": [0]}],
  "nodes": [{"mesh": 0, "name": "bubble_organic"}],
  "meshes": [{"name": "bubble", "primitives": [{
      "attributes": {"POSITION": 1, "NORMAL": 2, "TEXCOORD_0": 3},
      "indices": 0,
      "material": 0
  }]}],
  "materials": [{
    "name": "iridescent_bubble",
    "doubleSided": True,
    "alphaMode": "BLEND",
    "pbrMetallicRoughness": {
        "baseColorFactor": [0.55, 0.82, 1.0, 0.10],
        "metallicFactor": 0.05,
        "roughnessFactor": 0.0
    },
    "emissiveFactor": [0.18, 0.38, 0.72],
    "extensions": {
      "KHR_materials_transmission": {"transmissionFactor": 0.93},
      "KHR_materials_ior": {"ior": 1.45},
      "KHR_materials_iridescence": {
          "iridescenceFactor": 1.0,
          "iridescenceIor": 1.5,
          "iridescenceThicknessMinimum": 80.0,
          "iridescenceThicknessMaximum": 600.0
      }
    }
  }],
  "extensionsUsed": [
      "KHR_materials_transmission",
      "KHR_materials_ior",
      "KHR_materials_iridescence"
  ],
  "animations": [{
    "name": "pulse",
    "channels": [{"sampler": 0, "target": {"node": 0, "path": "scale"}}],
    "samplers": [{"input": 4, "interpolation": "LINEAR", "output": 5}]
  }],
  "accessors": [
    {"bufferView":0,"byteOffset":0,"componentType":5123,"count":ni,"type":"SCALAR"},
    {"bufferView":1,"byteOffset":0,"componentType":5126,"count":nv,"type":"VEC3","min":mn,"max":mx},
    {"bufferView":2,"byteOffset":0,"componentType":5126,"count":nv,"type":"VEC3"},
    {"bufferView":3,"byteOffset":0,"componentType":5126,"count":nv,"type":"VEC2"},
    {"bufferView":4,"byteOffset":0,"componentType":5126,"count":3,"type":"SCALAR","min":[0.0],"max":[2.0]},
    {"bufferView":5,"byteOffset":0,"componentType":5126,"count":3,"type":"VEC3"}
  ],
  "bufferViews": [
    {"buffer":0,"byteOffset":offsets[0],"byteLength":len(idx_bytes),"target":34963},
    {"buffer":0,"byteOffset":offsets[1],"byteLength":len(pos_bytes),"target":34962},
    {"buffer":0,"byteOffset":offsets[2],"byteLength":len(nor_bytes),"target":34962},
    {"buffer":0,"byteOffset":offsets[3],"byteLength":len(uv_bytes),"target":34962},
    {"buffer":0,"byteOffset":offsets[4],"byteLength":len(time_bytes)},
    {"buffer":0,"byteOffset":offsets[4]+len(time_bytes),"byteLength":len(scale_bytes)}
  ],
  "buffers": [{"byteLength": len(bin_data)}]
}

json_bytes = pad4(json.dumps(gltf, separators=(',',':')).encode(), b' ')
json_chunk = struct.pack('<II', len(json_bytes), 0x4E4F534A) + json_bytes
bin_chunk  = struct.pack('<II', len(bin_data),  0x004E4942) + bin_data
total = 12 + len(json_chunk) + len(bin_chunk)
header = struct.pack('<III', 0x46546C67, 2, total)

out = r"C:\Users\crisi\Downloads\Projetos Crisia\escultura-ar\bubble.glb"
with open(out, 'wb') as f:
    f.write(header + json_chunk + bin_chunk)
print(f"OK - {total} bytes -> {out}")
