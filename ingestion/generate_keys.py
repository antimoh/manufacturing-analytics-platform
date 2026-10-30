"""
Generate RSA Key Pair for Snowflake Authentication

This script generates an RSA key pair for secure, password-less authentication
to Snowflake. Key-pair authentication is the recommended approach for:
- Automated data pipelines
- CI/CD deployments
- Service accounts
- Any production workload

Usage:
    python ingestion/generate_keys.py
    python ingestion/generate_keys.py your_username  # Optional: pre-fill username

The script will:
1. Create ~/.snowflake directory if it doesn't exist
2. Generate a 2048-bit RSA key pair
3. Save private key to ~/.snowflake/rsa_key.p8
4. Save public key to ~/.snowflake/rsa_key.pub
5. Output the SQL command to register the public key in Snowflake

After running, copy the ALTER USER command and run it in Snowflake
(with ACCOUNTADMIN role) to enable key-pair authentication.
"""
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.backends import default_backend
from pathlib import Path
import os
import sys


def generate_snowflake_keys(username: str = None) -> None:
    """Generate RSA key pair for Snowflake authentication.
    
    Args:
        username: Snowflake username for the ALTER USER command.
                  If None, a placeholder is shown.
    """
    # Determine home directory (works on Windows and Unix)
    home = Path(os.environ.get('USERPROFILE', os.environ.get('HOME', '.')))
    snowflake_dir = home / '.snowflake'
    
    # Create directory if needed
    snowflake_dir.mkdir(exist_ok=True)
    print(f"Key directory: {snowflake_dir}")
    
    # Generate private key
    print("Generating 2048-bit RSA key pair...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    
    # Serialize private key (unencrypted for automated use)
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key
    public_key = private_key.public_key()
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    # Save keys to files
    private_key_path = snowflake_dir / 'rsa_key.p8'
    public_key_path = snowflake_dir / 'rsa_key.pub'
    
    private_key_path.write_bytes(private_pem)
    public_key_path.write_bytes(public_pem)
    
    print(f"✓ Private key saved: {private_key_path}")
    print(f"✓ Public key saved:  {public_key_path}")
    print()
    
    # Format public key for Snowflake (single line, no headers)
    pub_key_clean = public_pem.decode('utf-8')
    pub_key_clean = pub_key_clean.replace('-----BEGIN PUBLIC KEY-----', '')
    pub_key_clean = pub_key_clean.replace('-----END PUBLIC KEY-----', '')
    pub_key_clean = pub_key_clean.replace('\n', '').strip()
    
    # Output SQL command
    user_placeholder = username if username else '<YOUR_USERNAME>'
    
    print('=' * 70)
    print('NEXT STEP: Run this SQL in Snowflake Worksheets')
    print('=' * 70)
    print()
    print('-- Switch to ACCOUNTADMIN role (required for ALTER USER)')
    print('USE ROLE ACCOUNTADMIN;')
    print()
    print('-- Register the public key with your user')
    print(f'ALTER USER "{user_placeholder}" SET RSA_PUBLIC_KEY = \'{pub_key_clean}\';')
    print()
    print('-- Verify the key was set')
    print(f'DESC USER "{user_placeholder}";')
    print()
    print('=' * 70)
    print()
    print('IMPORTANT: Keep your private key secure!')
    print('- Never commit rsa_key.p8 to version control')
    print('- The ~/.snowflake directory should already be in .gitignore')
    print()


if __name__ == '__main__':
    # Allow optional username argument
    username = sys.argv[1] if len(sys.argv) > 1 else None
    generate_snowflake_keys(username)
