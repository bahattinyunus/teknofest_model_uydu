import zlib
import hashlib

class DataIntegrity:
    """
    Handles telemetry data integrity and security.
    Provides CRC32 and SHA256 checksums, and basic command verification.
    """

    @staticmethod
    def calculate_crc32(data: str) -> str:
        """Calculates CRC32 checksum for a string."""
        return hex(zlib.crc32(data.encode()) & 0xFFFFFFFF)

    @staticmethod
    def verify_crc32(data: str, checksum: str) -> bool:
        """Verifies data against a CRC32 checksum."""
        return DataIntegrity.calculate_crc32(data) == checksum

    @staticmethod
    def generate_packet_hash(packet_dict: dict) -> str:
        """Generates a SHA256 hash for a telemetry packet dictionary."""
        sorted_keys = sorted(packet_dict.keys())
        data_str = "|".join(f"{k}:{packet_dict[k]}" for k in sorted_keys)
        return hashlib.sha256(data_str.encode()).hexdigest()[:8]

    @staticmethod
    def encrypt_command(command: str, key: str = "TEKNOFEST_2025") -> str:
        """Basic XOR 'encryption' for sensitive commands (placeholder)."""
        return "".join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(command))

    @staticmethod
    def decrypt_command(encrypted_cmd: str, key: str = "TEKNOFEST_2025") -> str:
        """Decrypts XOR 'encrypted' command."""
        return DataIntegrity.encrypt_command(encrypted_cmd, key)
