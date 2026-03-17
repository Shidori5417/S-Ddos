import sys
from unittest.mock import MagicMock

# Mock dependencies that are missing in the environment
mock_core = MagicMock()
sys.modules['core'] = mock_core
sys.modules['core.utils'] = mock_core.utils
sys.modules['core.logger'] = mock_core.logger

# Mock layer4.attacks to avoid circular/broken imports during testing
sys.modules['layer4.attacks'] = MagicMock()
sys.modules['layer4.spoofing'] = MagicMock()
sys.modules['layer4.amplification'] = MagicMock()

import pytest
# Now import from the actual source
from layer4.packet_builder import PacketBuilder, PacketConfig

class MockPacketBuilder(PacketBuilder):
    def build_packet(self) -> bytes:
        return b""

    def build_header(self) -> bytes:
        return b""

@pytest.fixture
def packet_builder():
    config = PacketConfig(destination_ip="127.0.0.1")
    return MockPacketBuilder(config)

def test_calculate_checksum_standard(packet_builder):
    # Standard IP header-like data
    data = b'\x45\x00\x00\x3c\x1c\x46\x40\x00\x40\x06\x00\x00\xac\x10\x0a\x63\xac\x10\x0a\x0c'
    # The checksum field is 0x0000 in the data above.
    # For this specific data, the checksum should be 0xb1e6
    checksum = packet_builder.calculate_checksum(data)
    assert isinstance(checksum, int)
    assert 0 <= checksum <= 0xFFFF
    assert checksum == 0xb1e6

def test_calculate_checksum_odd_length(packet_builder):
    # Odd length data: 3 bytes
    data = b'\x01\x02\x03'
    # Should be padded to b'\x01\x02\x03\x00'
    # word1 = 0x0102, word2 = 0x0300
    # sum = 0x0402
    # ~sum & 0xFFFF = 0xFBFD
    checksum = packet_builder.calculate_checksum(data)
    assert checksum == 0xfbfd

def test_calculate_checksum_carry(packet_builder):
    # Data that causes carry
    data = b'\xff\xff\xff\xff'
    # word1 = 0xFFFF, word2 = 0xFFFF
    # sum = 0x1FFFE
    # checksum = (sum & 0xFFFF) + (sum >> 16) = 0xFFFE + 1 = 0xFFFF
    # result = ~0xFFFF & 0xFFFF = 0x0000
    checksum = packet_builder.calculate_checksum(data)
    assert checksum == 0x0000

def test_calculate_checksum_empty(packet_builder):
    data = b''
    # sum = 0
    # result = ~0 & 0xFFFF = 0xFFFF
    checksum = packet_builder.calculate_checksum(data)
    assert checksum == 0xffff
