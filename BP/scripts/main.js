import { world, system } from "@minecraft/server";

/**
 * SteadyCraft Accessibility & Motion Comfort Script Controller
 * Automatically manages stabilized camera perspective persistence and commands.
 */

const CAMERA_PRESETS = {
  right: "steadycraft:over_the_shoulder",
  left: "steadycraft:over_the_shoulder_left",
  center: "steadycraft:centered"
};

const DYNAMIC_PROPERTY_KEY = "steadycraft_cam_mode";

/**
 * Retrieves the stored camera mode for a player.
 * Defaults to "right" (over-the-shoulder right) if unset.
 */
function getPlayerCameraMode(player) {
  try {
    const saved = player.getDynamicProperty(DYNAMIC_PROPERTY_KEY);
    if (typeof saved === "string" && (CAMERA_PRESETS[saved] || saved === "off")) {
      return saved;
    }
  } catch (err) {
    // Dynamic property access fallback
  }
  return "right";
}

/**
 * Persists the preferred camera mode on the player entity.
 */
function setPlayerCameraMode(player, mode) {
  try {
    player.setDynamicProperty(DYNAMIC_PROPERTY_KEY, mode);
  } catch (err) {
    console.warn(`[SteadyCraft] Failed to save camera mode: ${err}`);
  }
}

/**
 * Applies the requested camera preset or clears back to vanilla.
 */
function applyCamera(player, mode) {
  if (!player.isValid()) return;

  if (mode === "off" || mode === "clear") {
    player.runCommandAsync("camera @s clear").catch(() => {});
    return;
  }

  const preset = CAMERA_PRESETS[mode] || CAMERA_PRESETS.right;
  player.runCommandAsync(`camera @s set ${preset}`).catch(() => {});
}

/**
 * Automatically applies the persistent camera preference when the player spawns
 * (covers world join, death respawn, and dimension transition).
 */
world.afterEvents.playerSpawn.subscribe((event) => {
  const player = event.player;
  if (!player) return;

  // Small delay to ensure the player entity and camera API are fully initialized
  system.runTimeout(() => {
    if (!player.isValid()) return;
    const mode = getPlayerCameraMode(player);
    if (mode !== "off") {
      applyCamera(player, mode);
    }
  }, 10);
});

/**
 * In-game command handler using Bedrock's native /scriptevent interface.
 * Usage:
 *   /scriptevent steadycraft:camera <right|left|center|off>
 *   /scriptevent steadycraft:help
 */
system.afterEvents.scriptEventReceive.subscribe((event) => {
  const { id, message, sourceEntity } = event;
  if (!id.startsWith("steadycraft:")) return;

  const player = sourceEntity;
  if (!player || !player.isValid()) return;

  const subCommand = id.replace("steadycraft:", "").trim().toLowerCase();
  const arg = (message || "").trim().toLowerCase();

  if (subCommand === "help") {
    player.sendMessage(
      "§a=== SteadyCraft Motion Comfort Settings ===\n" +
      "§e/scriptevent steadycraft:camera right  §7- Right shoulder view (Default)\n" +
      "§e/scriptevent steadycraft:camera left   §7- Left shoulder view\n" +
      "§e/scriptevent steadycraft:camera center §7- Centered stabilized 3rd person\n" +
      "§e/scriptevent steadycraft:camera off    §7- Disable (Restore vanilla 1st person)\n\n" +
      "§bRecommended Vanilla Settings for Sickness Prevention:\n" +
      "§f1. Video > Camera Shake: §cOFF\n" +
      "§f2. Accessibility > Distortion Effects: §c0%\n" +
      "§f3. Video/Accessibility > FOV Can Be Altered by Gameplay: §cOFF"
    );
    return;
  }

  if (subCommand === "camera") {
    if (arg === "left") {
      setPlayerCameraMode(player, "left");
      applyCamera(player, "left");
      player.sendMessage("§a[SteadyCraft] Switched to Left Shoulder perspective.");
    } else if (arg === "center" || arg === "centered") {
      setPlayerCameraMode(player, "center");
      applyCamera(player, "center");
      player.sendMessage("§a[SteadyCraft] Switched to Centered Stabilized perspective.");
    } else if (arg === "off" || arg === "clear" || arg === "vanilla") {
      setPlayerCameraMode(player, "off");
      applyCamera(player, "off");
      player.sendMessage("§e[SteadyCraft] Perspective disabled. Restored vanilla camera.");
    } else {
      // Default to right
      setPlayerCameraMode(player, "right");
      applyCamera(player, "right");
      player.sendMessage("§a[SteadyCraft] Switched to Right Shoulder perspective.");
    }
  }
});
