from dataclasses import dataclass
from typing import Optional, Dict
import re
from urllib.parse import urlparse, parse_qs

@dataclass
class LCTIdentity:
    """Parsed LCT presence record."""
    component: str
    instance: str
    role: str
    network: str
    version: str = "1.0.0"
    pairing_status: Optional[str] = None
    trust_threshold: Optional[float] = None
    capabilities: list[str] = None
    public_key_hash: Optional[str] = None

    @property
    def lct_uri(self) -> str:
        """Reconstruct LCT URI."""
        base = f"lct://{self.component}:{self.instance}:{self.role}@{self.network}"

        params = []
        if self.version != "1.0.0":
            params.append(f"version={self.version}")
        if self.pairing_status:
            params.append(f"pairing_status={self.pairing_status}")
        if self.trust_threshold is not None:
            params.append(f"trust_threshold={self.trust_threshold}")
        if self.capabilities:
            params.append(f"capabilities={','.join(self.capabilities)}")

        query_string = "&".join(params) if params else ""
        fragment = f"#{self.public_key_hash}" if self.public_key_hash else ""

        uri = base
        if query_string:
            uri += f"?{query_string}"
        if fragment:
            uri += fragment

        return uri

def parse_lct_uri(lct_uri: str) -> LCTIdentity:
    """
    Parse LCT URI into structured presence record.

    Args:
        lct_uri: LCT URI string (e.g., "lct://sage:thinker:expert_42@testnet")

    Returns:
        LCTIdentity object with parsed fields

    Raises:
        ValueError: If URI format is invalid
    """
    # Validate scheme
    if not lct_uri.startswith("lct://"):
        raise ValueError(f"Invalid LCT URI scheme: {lct_uri}")

    # Parse using urllib
    parsed = urlparse(lct_uri)

    # Extract authority (component:instance:role@network)
    authority = parsed.netloc
    path = parsed.path.lstrip("/")

    # Combine netloc and path for parsing
    full_authority = authority + "/" + path if path else authority

    # Pattern: component:instance:role@network
    pattern = r"^([^:]+):([^:]+):([^@]+)@([^?#]+)"
    match = re.match(pattern, full_authority)

    if not match:
        raise ValueError(f"Invalid LCT authority format: {full_authority}")

    component, instance, role, network = match.groups()

    # Parse query parameters
    query_params = parse_qs(parsed.query)
    version = query_params.get("version", ["1.0.0"])[0]
    pairing_status = query_params.get("pairing_status", [None])[0]
    trust_threshold_str = query_params.get("trust_threshold", [None])[0]
    trust_threshold = float(trust_threshold_str) if trust_threshold_str else None
    capabilities_str = query_params.get("capabilities", [None])[0]
    capabilities = capabilities_str.split(",") if capabilities_str else None

    # Parse fragment (public key hash)
    public_key_hash = parsed.fragment if parsed.fragment else None

    return LCTIdentity(
        component=component,
        instance=instance,
        role=role,
        network=network,
        version=version,
        pairing_status=pairing_status,
        trust_threshold=trust_threshold,
        capabilities=capabilities,
        public_key_hash=public_key_hash
    )

def validate_lct_uri(lct_uri: str) -> bool:
    """Validate LCT URI format."""
    try:
        parse_lct_uri(lct_uri)
        return True
    except ValueError:
        return False

# Example usage
if __name__ == "__main__":
    uri = "lct://sage:thinker:expert_42@testnet?version=1.0.0&pairing_status=active&trust_threshold=0.75#did:key:z6Mk..."

    lct = parse_lct_uri(uri)
    print(f"Component: {lct.component}")
    print(f"Instance: {lct.instance}")
    print(f"Role: {lct.role}")
    print(f"Network: {lct.network}")
    print(f"Trust Threshold: {lct.trust_threshold}")
    print(f"Reconstructed: {lct.lct_uri}")
