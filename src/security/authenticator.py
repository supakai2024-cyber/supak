import time
import hmac
import hashlib
import struct

class Authenticator:
    def __init__(self, secret_key: str = "ANTIGRAVITY_SECURE_KEY", interval: int = 15):
        """
        Initialize the Authenticator using a TOTP-like mechanism.
        
        Args:
            secret_key (str): The secret key for HMAC.
            interval (int): Time step in seconds (default 15s).
        """
        self.secret = secret_key
        self.interval = interval

    def generate_code(self, timestamp=None) -> str:
        """
        Generate a 6-digit code based on the current time (or provided timestamp).
        """
        if timestamp is None:
            timestamp = time.time()
        
        # Calculate time counter based on interval
        counter = int(timestamp // self.interval)
        
        # Convert counter to bytes (8 bytes, big-endian)
        counter_bytes = struct.pack(">Q", counter)
        
        # Create HMAC-SHA1 signature using the secret
        key_bytes = self.secret.encode('utf-8')
        hmac_digest = hmac.new(key_bytes, counter_bytes, hashlib.sha1).digest()
        
        # Dynamic Truncation
        offset = hmac_digest[-1] & 0x0F
        binary_code = (
            (hmac_digest[offset] & 0x7F) << 24 |
            (hmac_digest[offset + 1] & 0xFF) << 16 |
            (hmac_digest[offset + 2] & 0xFF) << 8 |
            (hmac_digest[offset + 3] & 0xFF)
        )
        
        # Generate 6-digit OTP
        otp = binary_code % 1_000_000
        return f"{otp:06d}"

    def verify_code(self, code: str, window: int = 1) -> bool:
        """
        Verify the provided code.
        
        Args:
            code (str): The code to verify.
            window (int): Number of intervals to check before/after.
        
        Returns:
            bool: True if valid, False otherwise.
        """
        current_time = time.time()
        
        # Check current, previous, and next windows
        for i in range(-window, window + 1):
            check_time = current_time + (i * self.interval)
            if self.generate_code(check_time) == code:
                return True
        return False

# Self-test if run standalone
if __name__ == "__main__":
    auth = Authenticator()
    code = auth.generate_code()
    print(f"Generated Code: {code}")
    print(f"Verify Result: {auth.verify_code(code)}")
