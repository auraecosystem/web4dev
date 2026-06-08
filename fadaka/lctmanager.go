message LinkedContextToken {
  string lct_id = 1;                    // Full LCT URI
  string component = 2;                 // Parsed component
  string instance = 3;                  // Parsed instance
  string role = 4;                      // Parsed role
  string network = 5;                   // Parsed network
  string pairing_status = 6;            // Current status
  google.protobuf.Timestamp created_at = 7;
  google.protobuf.Timestamp updated_at = 8;
  string public_key = 9;                // Cryptographic attestation key
  map<string, string> metadata = 10;    // Extensible metadata
  int32 version = 11;                   // Version for updates
}
