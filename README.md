# DramaClaw Skills

Community Skill repository for DramaClaw.

## Layout

Each published Skill lives in its own folder:

```text
skills/<skill-id>/bundle.json
skills/<skill-id>/cover.webp
```

`bundle.json` must use `schema_version: "dramaclaw.skill-bundle.v1"` and include one Skill plus the Recipes referenced by `skill.allowed_recipe_ids`.

## Local Checks

```bash
python3 -m unittest discover -s tests
python3 scripts/build_catalog.py validate --root . --allow-empty
python3 scripts/build_catalog.py build --root . --output catalog.json --allow-empty
```

The CI rejects unsafe Bundle content such as scripts, command/env fields, secrets, and hardcoded supplier model names.
ANIME STYLE: Makoto Shinkai + Demon Slayer, ultra detailed, cinematic 4K, 24fps

SCENE 1 - INTRO - 0:00-0:08
Visual: Night city, vertical neon signs, Camera Angle: Drone top shot slowly descending, SFX: Low city hum + distant notification sounds *pop pop*, Music: Lo-fi sad piano
Prompt: Tokyo-like futuristic city at night, holographic follower counts floating above people's heads like [1.2K] [10M], rain on neon lights

SCENE 2 - 0:08-0:18
Visual: Close up on MIKA, Camera Angle: 50mm eye-level close up, then rack focus to her hollow eyes, SFX: *click* of camera shutter, her heartbeat *dhak dhak* getting faster, Noise: Chat comments floating in air "so pretty!!"
Prompt: beautiful 17yo anime witch girl with silver hair, influencer outfit, sitting in bedroom doing live, eyes tired, follower count 10,000,000 glowing above her, dark circles, ultra realistic skin texture

SCENE 3 - 0
