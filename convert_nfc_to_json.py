#!/usr/bin/env python3
"""
Convert Flipper Zero NFC files to Android-friendly JSON format
"""
import os
import json
import re
from pathlib import Path

def parse_flipper_nfc_file(file_path):
    """Parse a Flipper Zero NFC file and extract all data"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data = {
        'uid': None,
        'atqa': None,
        'sak': None,
        'mifare_type': None,
        'blocks': []
    }
    
    # Extract UID - match until end of line to avoid capturing next line
    uid_match = re.search(r'UID:\s*([0-9A-F\s]+?)(?:\n|$)', content, re.IGNORECASE | re.MULTILINE)
    if uid_match:
        uid_str = uid_match.group(1).strip()
        # Clean UID: remove ALL whitespace and non-hex characters
        data['uid'] = re.sub(r'[^0-9A-F]', '', uid_str, flags=re.IGNORECASE).upper()
    
    # Extract ATQA
    atqa_match = re.search(r'ATQA:\s*([0-9A-F\s]+)', content)
    if atqa_match:
        atqa_str = atqa_match.group(1).strip()
        data['atqa'] = ''.join(c for c in atqa_str if c in '0123456789ABCDEFabcdef').upper()
    
    # Extract SAK
    sak_match = re.search(r'SAK:\s*([0-9A-F\s]+)', content)
    if sak_match:
        sak_str = sak_match.group(1).strip()
        data['sak'] = ''.join(c for c in sak_str if c in '0123456789ABCDEFabcdef').upper()
    
    # Extract Mifare type
    mifare_match = re.search(r'Mifare Classic type:\s*(\w+)', content)
    if mifare_match:
        data['mifare_type'] = mifare_match.group(1)
    
    # Extract all blocks
    # Match block lines more carefully - each block is on a single line
    # Pattern: "Block N: XX XX XX ..." where XX are hex pairs (exactly 16 pairs = 32 hex chars)
    block_pattern = r'Block\s+(\d+):\s*((?:[0-9A-F]{2}\s*){16})'
    blocks = {}
    for match in re.finditer(block_pattern, content, re.MULTILINE | re.IGNORECASE):
        block_num = int(match.group(1))
        # Clean the block data: remove ALL whitespace (spaces, tabs, newlines) and convert to uppercase
        block_data = re.sub(r'\s+', '', match.group(2)).upper()
        # Ensure it's exactly 32 hex characters (16 bytes)
        if len(block_data) == 32:
            blocks[block_num] = block_data
        elif len(block_data) > 32:
            # If too long, take first 32 characters (might have trailing whitespace/newline)
            blocks[block_num] = block_data[:32]
            print(f"Warning: Block {block_num} had {len(block_data)} chars, truncated to 32")
        else:
            print(f"Warning: Block {block_num} has invalid length: {len(block_data)} (expected 32)")
    
    # Convert to array format (ensure all 64 blocks are present)
    for i in range(64):
        if i in blocks:
            data['blocks'].append(blocks[i])
        else:
            data['blocks'].append('00' * 16)  # Empty block
    
    return data

def convert_all_nfc_files(source_dir, output_dir):
    """Convert all NFC files from source to output directory"""
    source_path = Path(source_dir)
    output_path = Path(output_dir)
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Find all .nfc files
    nfc_files = list(source_path.rglob('*.nfc'))
    
    print(f"Found {len(nfc_files)} NFC files to convert...")
    
    converted_count = 0
    errors = []
    
    for nfc_file in nfc_files:
        try:
            # Parse the NFC file
            nfc_data = parse_flipper_nfc_file(nfc_file)
            
            if not nfc_data['uid']:
                errors.append((str(nfc_file), "Missing UID"))
                continue
            
            # Get relative path from source directory
            rel_path = nfc_file.relative_to(source_path)
            
            # Create output path structure
            output_file = output_path / rel_path.with_suffix('.json')
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Extract category and subcategory from path
            parts = rel_path.parts
            category = parts[0] if len(parts) > 0 else None
            subcategory = parts[1] if len(parts) > 1 else None
            
            # Add metadata
            nfc_data['metadata'] = {
                'original_filename': nfc_file.name,
                'original_path': str(rel_path).replace('\\', '/'),
                'category': category,
                'subcategory': subcategory
            }
            
            # Write JSON file
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(nfc_data, f, indent=2)
            
            converted_count += 1
            if converted_count % 50 == 0:
                print(f"Converted {converted_count}/{len(nfc_files)} files...")
                
        except Exception as e:
            errors.append((str(nfc_file), str(e)))
            print(f"Error converting {nfc_file}: {e}")
    
    print(f"\nConversion complete!")
    print(f"Successfully converted: {converted_count} files")
    print(f"Errors: {len(errors)}")
    if errors:
        print("\nFirst 10 errors:")
        for file, error in errors[:10]:
            print(f"  {file}: {error}")
    
    return converted_count, errors

if __name__ == '__main__':
    # Set source and output directories
    script_dir = Path(__file__).parent
    source_directory = script_dir
    output_directory = script_dir / 'skywriter' / 'app' / 'src' / 'main' / 'assets' / 'Android_NFC_Data'
    
    convert_all_nfc_files(source_directory, output_directory)

