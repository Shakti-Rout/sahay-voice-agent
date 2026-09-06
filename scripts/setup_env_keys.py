import os
from pathlib import Path

def setup_keys():
    source_path = Path(r"C:\Users\SAMBIT\OneDrive\Documents\API KEYS.txt")
    target_env = Path(__file__).resolve().parent.parent / "backend" / ".env"
    example_env = Path(__file__).resolve().parent.parent / ".env.example"

    if not source_path.exists():
        print(f"[Error] Source file not found: {source_path}")
        return False

    source_content = source_path.read_text(encoding="utf-8", errors="ignore")
    
    # Read example env to get default structure
    env_content = example_env.read_text(encoding="utf-8") if example_env.exists() else ""
    
    # Parse source lines (handling KEY=VALUE, KEY: VALUE, etc.)
    key_map = {}
    for line in source_content.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            parts = line.split("=", 1)
            k, v = parts[0].strip(), parts[1].strip()
            key_map[k.upper()] = v
        elif ":" in line:
            parts = line.split(":", 1)
            k, v = parts[0].strip(), parts[1].strip()
            key_map[k.upper()] = v

    # Match and replace in env_content
    # Mapping common aliases
    alias_map = {
        "GEMINI_API_KEY": ["GEMINI_API_KEY", "GEMINI_KEY", "GOOGLE_API_KEY", "GEMINI"],
        "SARVAM_API_KEY": ["SARVAM_API_KEY", "SARVAM_KEY", "SARVAM"],
        "EXOTEL_ACCOUNT_SID": ["EXOTEL_ACCOUNT_SID", "EXOTEL_SID"],
        "EXOTEL_API_KEY": ["EXOTEL_API_KEY", "EXOTEL_KEY"],
        "EXOTEL_API_TOKEN": ["EXOTEL_API_TOKEN", "EXOTEL_TOKEN"],
        "EXOTEL_VIRTUAL_NUMBER": ["EXOTEL_VIRTUAL_NUMBER", "EXOPHONE", "EXOTEL_PHONE"],
        "BHASHINI_API_KEY": ["BHASHINI_API_KEY", "BHASHINI_KEY"],
        "BHASHINI_USER_ID": ["BHASHINI_USER_ID", "BHASHINI_USER"],
        "BHASHINI_AUTH_TOKEN": ["BHASHINI_AUTH_TOKEN", "BHASHINI_TOKEN"],
        "SUPABASE_URL": ["SUPABASE_URL", "SUPABASE_PROJECT_URL"],
        "SUPABASE_ANON_KEY": ["SUPABASE_ANON_KEY", "SUPABASE_KEY", "SUPABASE_PUBLIC_KEY"],
        "SUPABASE_SERVICE_ROLE_KEY": ["SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SERVICE_KEY"]
    }

    matched_keys = []
    lines = env_content.splitlines()
    new_lines = []
    
    for line in lines:
        replaced = False
        for target_key, aliases in alias_map.items():
            if line.startswith(f"{target_key}="):
                for alias in aliases:
                    if alias in key_map:
                        new_lines.append(f'{target_key}="{key_map[alias]}"')
                        matched_keys.append(target_key)
                        replaced = True
                        break
                if replaced:
                    break
        if not replaced:
            new_lines.append(line)

    target_env.write_text("\n".join(new_lines), encoding="utf-8")
    print(f"[Success] Environment configured at {target_env}")
    print(f"[Configured Keys] {', '.join(matched_keys)}")
    return True

if __name__ == "__main__":
    setup_keys()
