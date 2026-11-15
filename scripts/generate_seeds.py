"""
Seed Generator Script (Section 10 Requirement)
Generates Argon2 hashes for seed passwords.
"""
from pwdlib import PasswordHash

pwd_context = PasswordHash.recommended()

def get_hashes():
    return {
        "admin": pwd_context.hash("admin123"),
        "guard": pwd_context.hash("guard123"),
        "resident": pwd_context.hash("resident123")
    }

if __name__ == "__main__":
    print("Demo Password Hashes:")
    for user, h in get_hashes().items():
        print(f"  {user}: {h}")
