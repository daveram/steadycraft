# SteadyCraft 🧭

> **Accessibility & Simulation Sickness Prevention Add-On for Minecraft: Bedrock Edition**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Minecraft: Bedrock](https://img.shields.io/badge/Minecraft%20Bedrock-1.21%2B-green.svg)](https://minecraft.net)

---

## 🔬 The Problem: First-Person Simulation Sickness

First-person motion sickness (vestibular-ocular sensory conflict) in Minecraft is triggered primarily by:
1. **Vertical Terrain Snapping**: Instantaneous jumping/stepping up blocks, stairs, and slabs without physical vestibular cues.
2. **Peripheral Optical Flow**: High-velocity visual movement at the edges of the screen during camera turning without a grounded visual reference anchor.
3. **Involuntary Camera Displacements**: Hurt-tilt/damage shake, dynamic FOV punching (sprinting/swiftness/speed effects), and nauseating portal/nausea screen-warp shaders.

Traditional Java solutions rely on client-side bytecode injection (Fabric/Mixins), while server-side tick loops (20 Hz) cause stutter. **SteadyCraft** solves this natively for Bedrock players using the modern **Bedrock Cameras API**, **Script API persistence**, **JSON UI stabilization**, and **texture neutralization** with zero frame-pacing compromises.

---

## ✨ Features

- **Stabilized Over-The-Shoulder Perspective**:
  - Anchors the player model in the frame to serve as a constant, grounded visual reference point.
  - Dampens perceived vertical stepping snapping.
  - Disables client-side camera shake propagation (`player_effects: false`).
- **Out-of-the-Box Auto-Activation & Persistence**:
  - Automatically applies upon spawning, joining, respawning after death, or transitioning dimensions (Nether/End).
  - Remembers each player's individual camera preference across sessions.
- **In-Game Command Configuration**:
  - Switch camera angles on the fly via Bedrock's native `/scriptevent` interface without needing server operator or cheats enabled.
- **Visual Stabilization Overrides**:
  - **Static HUD Reticle Anchor**: Centered optical fixation point that keeps gaze anchored during head rotation.
  - **Peripheral Vignette**: Soft edge darkening that dampens high-velocity peripheral flow.
  - **Shader Neutralization**: Disables sickening nausea and portal warping shaders.

---

## 🎮 In-Game Controls & Commands

### Quick Commands (Script API)
Run these commands in chat at any time:

| Command | Action | Description |
| :--- | :--- | :--- |
| `/scriptevent steadycraft:camera right` | **Right Shoulder (Default)** | Offsets camera over the right shoulder (`[0.65, 0.2, -1.8]`). |
| `/scriptevent steadycraft:camera left` | **Left Shoulder** | Offsets camera over the left shoulder (`[-0.65, 0.2, -1.8]`). |
| `/scriptevent steadycraft:camera center` | **Centered 3rd-Person** | Centered stabilized chase cam (`[0.0, 0.35, -2.0]`). |
| `/scriptevent steadycraft:camera off` | **Disable / Vanilla** | Restores vanilla 1st-person camera and persists preference. |
| `/scriptevent steadycraft:help` | **Help Menu** | Prints command help and recommended accessibility settings to chat. |

### Direct Vanilla Camera Commands (Operators / Cheats)
If you prefer standard vanilla commands:
- Enable: `/camera @s set steadycraft:over_the_shoulder`
- Reset: `/camera @s clear`

---

## ⚙️ Recommended Vanilla Client Settings

For maximum nausea and motion sickness reduction, configure the following settings in your Minecraft Bedrock client:

| Setting Category | Option | Recommended Value | Reason |
| :--- | :--- | :--- | :--- |
| **Video** | **Camera Shake** | **`OFF`** | Eliminates involuntary screen shaking on explosions, sprinting, and riding. |
| **Accessibility** | **Distortion Effects** | **`0%`** | Disables portal warping and nausea wave effects. |
| **Video / Accessibility** | **FOV Can Be Altered by Gameplay** | **`OFF`** | Prevents sudden FOV changes when sprinting or under potion effects. |
| **Video** | **View Bobbing** | **`OFF`** | Removes walking view bounce if sensitive to rhythmic head motion. |

---

## 📦 Installation

### 1-Click Install (Recommended)
1. Download **`SteadyCraft_v<version>.mcaddon`** from the [Releases](https://github.com/daveram/steadycraft/releases) page.
2. Double-click or open the `.mcaddon` file with Minecraft.
3. Minecraft will automatically import both the **Behavior Pack (BP)** and **Resource Pack (RP)**.
4. When creating or editing a world:
   - Add **SteadyCraft BP** under **Behavior Packs**.
   - Add **SteadyCraft RP** under **Resource Packs**.
   - Ensure the packs are active and launch your world!

### Dedicated Server / Realms Setup
- Copy `SteadyCraft_BP` into `behavior_packs/` and `SteadyCraft_RP` into `resource_packs/`.
- Add both pack UUIDs to `world_behavior_packs.json` and `world_resource_packs.json`.

---

## 🛠️ Building & Packaging from Source

SteadyCraft includes a cross-platform packaging script that validates JSON syntax, verifies UUID uniqueness, and produces ready-to-distribute `.mcpack` and `.mcaddon` archives.

### Requirements
- Python 3.8+ (no third-party dependencies required)
- Bash (optional wrapper)

### Build Commands
```bash
# Using the shell wrapper
chmod +x build.sh
./build.sh

# Or directly with Python
python3 build.py
```

### Build Artifacts
Output packages will be generated inside the `dist/` directory:
- `dist/SteadyCraft_BP_v<version>.mcpack` — Behavior Pack archive.
- `dist/SteadyCraft_RP_v<version>.mcpack` — Resource Pack archive.
- `dist/SteadyCraft_v<version>.mcaddon` — Combined one-click bundle containing both packs.

---

## 📂 Repository Structure

```
steadycraft/
├── .github/
│   └── workflows/
│       └── release.yml              # Automated release workflow on tag push
├── BP/                              # Behavior Pack
│   ├── cameras/
│   │   └── presets/
│   │       ├── over_the_shoulder.json
│   │       ├── over_the_shoulder_left.json
│   │       └── centered.json
│   ├── scripts/
│   │   └── main.js                  # Script API persistence & /scriptevent handler
│   ├── manifest.json
│   └── pack_icon.png
├── RP/                              # Resource Pack
│   ├── textures/
│   │   ├── misc/
│   │   │   ├── nausea.png           # Transparent nausea shader override
│   │   │   └── underwater.png       # Clear underwater overlay
│   │   └── ui/
│   │       ├── reticle_anchor.png   # Central gaze anchor
│   │       └── vignette.png         # Peripheral optical flow dampener
│   ├── ui/
│   │   ├── _ui_defs.json
│   │   └── hud_screen.json          # HUD overlay definitions
│   ├── manifest.json
│   └── pack_icon.png
├── build.py                         # Cross-platform build & verification script
├── build.sh                         # Shell wrapper for build.py
├── .gitignore
├── LICENSE                          # MIT License
└── README.md
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) © 2026 Steven Shaw and contributors.
