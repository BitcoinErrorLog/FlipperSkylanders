#!/usr/bin/env python3
"""
Character Data Enrichment Script

This script helps populate character profiles with:
- Element (Fire, Water, Earth, Air, Life, Undead, Tech, Magic, Light, Dark)
- Biography/Description
- Abilities
- Character Type (Core, Giant, Swapper, Trap Master, etc.)

Usage:
    python enrich_character_data.py [--input-dir skywriter/app/src/main/assets/Android_NFC_Data] [--interactive]

The script will:
1. Read existing JSON files
2. For each character, try to match it with known character data
3. Add element, biography, abilities, and character type
4. Save enriched JSON files back

You can run in interactive mode to manually add data for characters.
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional

# Character database - you can expand this with more characters
CHARACTER_DATABASE = {
    # Skylanders 1 - Spyro's Adventure
    "Spyro": {
        "element": "Magic",
        "biography": "A brave purple dragon who protects the Skylands with his fire breath and determination. Spyro is the legendary hero of the Skylands.",
        "abilities": ["Fire Breath", "Charge Attack", "Dragon Flight"],
        "character_type": "Core"
    },
    "Bash": {
        "element": "Earth",
        "biography": "A powerful triceratops who uses his massive horns and tail to crush enemies. Bash is known for his strength and durability.",
        "abilities": ["Horn Charge", "Tail Swipe", "Earthquake"],
        "character_type": "Core"
    },
    "Boomer": {
        "element": "Tech",
        "biography": "A mechanical troll who throws explosive boomerangs. Boomer combines ancient troll magic with modern technology.",
        "abilities": ["Boomerang Throw", "Explosive Attack", "Tech Shield"],
        "character_type": "Core"
    },
    "Camo": {
        "element": "Life",
        "biography": "A plant-based creature who can blend into nature and attack from stealth. Camo uses nature's power to protect the Skylands.",
        "abilities": ["Stealth Attack", "Vine Whip", "Nature's Wrath"],
        "character_type": "Core"
    },
    "Chop-Chop": {
        "element": "Undead",
        "biography": "A skeletal warrior who wields dual swords with deadly precision. Chop-Chop is a master of close combat.",
        "abilities": ["Dual Sword Slash", "Bone Shield", "Undead Strike"],
        "character_type": "Core"
    },
    "Cynder": {
        "element": "Undead",
        "biography": "A dark dragon who was once evil but now fights for good. Cynder uses shadow and darkness as her weapons.",
        "abilities": ["Shadow Breath", "Dark Flight", "Shadow Strike"],
        "character_type": "Core"
    },
    "Dino-Rang": {
        "element": "Earth",
        "biography": "A dinosaur who throws boomerangs with incredible accuracy. Dino-Rang combines ancient power with modern combat.",
        "abilities": ["Boomerang Throw", "Earth Slam", "Precision Strike"],
        "character_type": "Core"
    },
    "Double Trouble": {
        "element": "Magic",
        "biography": "A two-headed wizard who casts powerful spells. Double Trouble's dual minds make them unpredictable in battle.",
        "abilities": ["Magic Blast", "Dual Spell", "Mystic Shield"],
        "character_type": "Core"
    },
    "Drill Sergeant": {
        "element": "Tech",
        "biography": "A robotic drill sergeant who commands with authority and precision. Drill Sergeant uses military tactics and technology.",
        "abilities": ["Drill Attack", "Command Strike", "Tech Blast"],
        "character_type": "Core"
    },
    "Drobot": {
        "element": "Tech",
        "biography": "A robotic dragon who combines the power of dragons with advanced technology. Drobot is a high-tech guardian.",
        "abilities": ["Laser Breath", "Tech Flight", "System Overload"],
        "character_type": "Core"
    },
    "Eruptor": {
        "element": "Fire",
        "biography": "A living volcano who spews lava and fire. Eruptor's explosive temper matches his explosive power.",
        "abilities": ["Lava Blast", "Fire Eruption", "Magma Strike"],
        "character_type": "Core"
    },
    "FlameSlinger": {
        "element": "Fire",
        "biography": "An elf archer who shoots flaming arrows with perfect accuracy. FlameSlinger is a master of fire and precision.",
        "abilities": ["Flaming Arrow", "Fire Shot", "Precision Strike"],
        "character_type": "Core"
    },
    "Ghost Roaster": {
        "element": "Undead",
        "biography": "A ghostly warrior who haunts the battlefield. Ghost Roaster can phase through attacks and strike from the shadows.",
        "abilities": ["Phantom Strike", "Ghost Form", "Soul Drain"],
        "character_type": "Core"
    },
    "Gill Grunt": {
        "element": "Water",
        "biography": "A fish soldier who fights with water cannons and harpoons. Gill Grunt is a master of aquatic combat.",
        "abilities": ["Water Cannon", "Harpoon Shot", "Aqua Blast"],
        "character_type": "Core"
    },
    "Hex": {
        "element": "Undead",
        "biography": "A skeletal sorceress who casts dark magic. Hex combines necromancy with powerful spellcasting.",
        "abilities": ["Dark Magic", "Bone Shield", "Necromancy"],
        "character_type": "Core"
    },
    "Ignitor": {
        "element": "Fire",
        "biography": "A fire knight who wields a flaming sword. Ignitor is a noble warrior who fights with honor and fire.",
        "abilities": ["Flaming Sword", "Fire Charge", "Knight's Valor"],
        "character_type": "Core"
    },
    "Lightning Rod": {
        "element": "Air",
        "biography": "A lightning-powered warrior who controls storms. Lightning Rod harnesses the power of thunder and lightning.",
        "abilities": ["Lightning Strike", "Thunder Blast", "Storm Control"],
        "character_type": "Core"
    },
    "Prism Break": {
        "element": "Earth",
        "biography": "A crystal warrior who uses light and earth. Prism Break refracts light through crystals to create powerful attacks.",
        "abilities": ["Crystal Blast", "Light Refraction", "Earth Crystal"],
        "character_type": "Core"
    },
    "Slam Bam": {
        "element": "Water",
        "biography": "A yeti who fights with ice and water. Slam Bam combines brute strength with elemental power.",
        "abilities": ["Ice Slam", "Water Blast", "Frost Strike"],
        "character_type": "Core"
    },
    "Sonic Boom": {
        "element": "Air",
        "biography": "A bat who uses sonic waves to attack. Sonic Boom's powerful screech can shatter enemies.",
        "abilities": ["Sonic Screech", "Air Blast", "Wing Strike"],
        "character_type": "Core"
    },
    "Stealth Elf": {
        "element": "Life",
        "biography": "A ninja elf who moves in shadows. Stealth Elf is a master of stealth and precision strikes.",
        "abilities": ["Stealth Attack", "Shadow Strike", "Elf Precision"],
        "character_type": "Core"
    },
    "Stump Smash": {
        "element": "Life",
        "biography": "A tree warrior who uses nature's power. Stump Smash combines plant magic with physical strength.",
        "abilities": ["Root Strike", "Nature's Wrath", "Tree Slam"],
        "character_type": "Core"
    },
    "Sunburn": {
        "element": "Fire",
        "biography": "A phoenix who rises from ashes. Sunburn combines fire and air elements in powerful attacks.",
        "abilities": ["Fire Flight", "Phoenix Strike", "Flame Rebirth"],
        "character_type": "Core"
    },
    "Terrafin": {
        "element": "Earth",
        "biography": "A shark who burrows through earth. Terrafin combines aquatic power with earth manipulation.",
        "abilities": ["Earth Burrow", "Shark Strike", "Ground Slam"],
        "character_type": "Core"
    },
    "Trigger Happy": {
        "element": "Tech",
        "biography": "A gun-slinging troll who never runs out of ammo. Trigger Happy is a master of rapid-fire combat.",
        "abilities": ["Rapid Fire", "Gun Blast", "Tech Precision"],
        "character_type": "Core"
    },
    "Voodood": {
        "element": "Magic",
        "biography": "A voodoo shaman who casts powerful curses. Voodood uses dark magic and voodoo dolls in battle.",
        "abilities": ["Voodoo Curse", "Dark Magic", "Shaman Strike"],
        "character_type": "Core"
    },
    "Warnado": {
        "element": "Air",
        "biography": "A tornado warrior who controls wind. Warnado spins into battle with devastating force.",
        "abilities": ["Tornado Spin", "Wind Blast", "Air Strike"],
        "character_type": "Core"
    },
    "Wham Shell": {
        "element": "Water",
        "biography": "A shell warrior who fights with water and shells. Wham Shell uses his shell as both weapon and shield.",
        "abilities": ["Shell Strike", "Water Blast", "Shell Shield"],
        "character_type": "Core"
    },
    "Whirlwind": {
        "element": "Air",
        "biography": "A unicorn who controls wind and rainbows. Whirlwind combines air magic with healing powers.",
        "abilities": ["Rainbow Blast", "Wind Strike", "Healing Rain"],
        "character_type": "Core"
    },
    "Wrecking Ball": {
        "element": "Earth",
        "biography": "A mole who rolls into battle. Wrecking Ball uses his round body as a devastating weapon.",
        "abilities": ["Roll Attack", "Earth Burrow", "Ball Slam"],
        "character_type": "Core"
    },
    "Zap": {
        "element": "Water",
        "biography": "An electric eel who controls water and electricity. Zap combines aquatic and electric powers.",
        "abilities": ["Electric Blast", "Water Strike", "Shock Attack"],
        "character_type": "Core"
    },
    "Zook": {
        "element": "Life",
        "biography": "A musician who uses sound waves. Zook combines music magic with nature's power.",
        "abilities": ["Sound Blast", "Music Magic", "Nature's Song"],
        "character_type": "Core"
    },
    
    # Giants
    "Bouncer": {
        "element": "Tech",
        "biography": "A giant robot who towers over enemies. Bouncer uses massive strength and technology to dominate the battlefield.",
        "abilities": ["Giant Slam", "Tech Blast", "Massive Strike"],
        "character_type": "Giant"
    },
    "Crusher": {
        "element": "Earth",
        "biography": "A giant golem made of stone. Crusher crushes everything in his path with earth-shattering power.",
        "abilities": ["Stone Slam", "Earthquake", "Giant Strike"],
        "character_type": "Giant"
    },
    "Eye-Brawl": {
        "element": "Undead",
        "biography": "A giant cyclops with a floating eye. Eye-Brawl combines brute strength with mystical vision.",
        "abilities": ["Giant Strike", "Eye Blast", "Undead Power"],
        "character_type": "Giant"
    },
    "Hot Head": {
        "element": "Fire",
        "biography": "A giant fire demon who burns everything. Hot Head's flames are as hot as his temper.",
        "abilities": ["Fire Blast", "Giant Slam", "Inferno"],
        "character_type": "Giant"
    },
    "Ninjini": {
        "element": "Magic",
        "biography": "A giant genie who grants wishes and fights with magic. Ninjini combines genie magic with ninja skills.",
        "abilities": ["Magic Blast", "Genie Strike", "Wish Power"],
        "character_type": "Giant"
    },
    "Swarm": {
        "element": "Life",
        "biography": "A giant bug who commands insects. Swarm uses nature's power and insect armies in battle.",
        "abilities": ["Swarm Attack", "Insect Strike", "Nature's Wrath"],
        "character_type": "Giant"
    },
    "Thumpback": {
        "element": "Water",
        "biography": "A giant whale warrior who controls water. Thumpback uses massive size and aquatic power.",
        "abilities": ["Water Blast", "Giant Slam", "Whale Strike"],
        "character_type": "Giant"
    },
    "Tree Rex": {
        "element": "Life",
        "biography": "A giant tree warrior who protects nature. Tree Rex combines plant magic with massive strength.",
        "abilities": ["Root Strike", "Giant Slam", "Nature's Wrath"],
        "character_type": "Giant"
    },
}

def normalize_name(name: str) -> str:
    """Normalize character name for matching."""
    # Remove common suffixes and variants (more comprehensive)
    variants = [
        " (Blue)", " (Legendary)", " (Silver)", " (Gold)", " (Red)", " (Clear)",
        " (GITD)", " (Metallic Purple)", " (Pearl)", " (Chrome)", " (Dark)", 
        " (Flocked)", " (Sidekick)", " (SideKick)", " (Halloween)", " (Sparkle)",
        " (Scarlet)", " (Gnarly)", " (Granite)", " (Meatallic Purple)",
        " (Series 2)", " (Series 3)", " (Series 4)", " (Eons Elite)",
        " (Spring)", " (Mini)", " (Legendary Bone Bash)", " (Bone Bash)",
        " (Dark Sure Shot)", " (Shark Shooter)", " (Power Blue Double Dare)",
        " (Lava Lance)", " (Deep Dive)", " (Double Dare)", " (Sure Shot)",
        " (Bronze Bottom)", " (Gold Bottom)", " Top", " Bottom"
    ]
    for variant in variants:
        name = name.replace(variant, "")
    
    # Remove series numbers and special characters
    import re
    name = re.sub(r'\s*\(Series\s+\d+\)', '', name, flags=re.IGNORECASE)
    name = name.replace("-", " ").replace("_", " ").strip()
    
    # Handle special cases
    name = name.replace("Crash Bash", "Bash")
    name = name.replace("Weeruptor", "Eruptor")
    
    return name

def find_character_data(character_name: str) -> Optional[Dict]:
    """Find character data in database."""
    normalized = normalize_name(character_name)
    
    # Direct match
    if normalized in CHARACTER_DATABASE:
        return CHARACTER_DATABASE[normalized]
    
    # Partial match
    for key, value in CHARACTER_DATABASE.items():
        if key.lower() in normalized.lower() or normalized.lower() in key.lower():
            return value
    
    return None

def enrich_json_file(file_path: Path, interactive: bool = False) -> bool:
    """Enrich a single JSON file with character data."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metadata = data.get("metadata", {})
        character_name = metadata.get("original_filename", "").replace(".nfc", "")
        
        # Check if already enriched
        if metadata.get("element") and metadata.get("biography"):
            print(f"  ✓ {character_name} already has profile data")
            return False
        
        # Find character data
        char_data = find_character_data(character_name)
        
        if char_data:
            # Add character data
            metadata["element"] = char_data["element"]
            metadata["biography"] = char_data["biography"]
            metadata["abilities"] = char_data["abilities"]
            metadata["character_type"] = char_data["character_type"]
            
            print(f"  ✓ Enriched {character_name} ({char_data['element']})")
        elif interactive:
            # Interactive mode - ask user for data
            print(f"\n  Character: {character_name}")
            element = input("    Element (Fire/Water/Earth/Air/Life/Undead/Tech/Magic/Light/Dark): ").strip()
            biography = input("    Biography: ").strip()
            abilities_str = input("    Abilities (comma-separated): ").strip()
            character_type = input("    Type (Core/Giant/Swapper/etc): ").strip()
            
            if element:
                metadata["element"] = element
            if biography:
                metadata["biography"] = biography
            if abilities_str:
                metadata["abilities"] = [a.strip() for a in abilities_str.split(",")]
            if character_type:
                metadata["character_type"] = character_type
            
            print(f"  ✓ Added data for {character_name}")
        else:
            print(f"  ✗ No data found for {character_name}")
            return False
        
        # Save enriched JSON
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return True
    except Exception as e:
        print(f"  ✗ Error processing {file_path}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Enrich character JSON files with profile data")
    parser.add_argument("--input-dir", default="skywriter/app/src/main/assets/Android_NFC_Data",
                       help="Directory containing JSON files")
    parser.add_argument("--interactive", action="store_true",
                       help="Interactive mode to manually add data")
    
    args = parser.parse_args()
    
    input_dir = Path(args.input_dir)
    if not input_dir.exists():
        print(f"Error: Directory {input_dir} does not exist")
        sys.exit(1)
    
    print(f"Enriching character data in {input_dir}")
    print("=" * 60)
    
    json_files = list(input_dir.rglob("*.json"))
    print(f"Found {len(json_files)} JSON files\n")
    
    enriched_count = 0
    for json_file in json_files:
        if enrich_json_file(json_file, args.interactive):
            enriched_count += 1
    
    print("\n" + "=" * 60)
    print(f"Enriched {enriched_count} out of {len(json_files)} files")
    print("\nNote: You can run with --interactive to manually add data for missing characters")

if __name__ == "__main__":
    main()

