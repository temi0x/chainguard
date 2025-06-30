import json
import os
from typing import List, Optional, Dict
from pathlib import Path

class ProtocolValidator:
    """
    Validates and normalizes protocol names against supported protocols list.
    Handles fuzzy matching and protocol name variations.
    """
    
    def __init__(self, protocols_file: str = "protocols.json"):
        self.protocols_file = protocols_file
        self.supported_protocols = self._load_protocols()
        self._create_mapping()
    
    def _load_protocols(self) -> List[str]:
        """Load supported protocols from JSON file"""
        try:
            protocols_path = Path(self.protocols_file)
            if not protocols_path.exists():
                protocols_path = Path(__file__).parent.parent / self.protocols_file
            
            with open(protocols_path, 'r') as f:
                protocols = json.load(f)
            
            if not protocols:
                raise ValueError("Empty protocols list")
                
            return protocols
        except Exception as e:
            print(f"Error loading protocols: {e}")
            # Fallback to hardcoded list
            return [
                "Aave V3", "Lido", "EigenLayer", "Ethena", 
                "Pendle Finance", "Uniswap V4"
            ]
    
    def _create_mapping(self):
        """Create mapping for fuzzy protocol name matching"""
        self.protocol_mapping = {}
        
        for protocol in self.supported_protocols:
            # Original name
            key = protocol.lower().strip()
            self.protocol_mapping[key] = protocol
            
            # Common variations
            variations = self._generate_variations(protocol)
            for variation in variations:
                self.protocol_mapping[variation.lower().strip()] = protocol
    
    def _generate_variations(self, protocol_name: str) -> List[str]:
        """Generate common variations of protocol names"""
        variations = []
        name_lower = protocol_name.lower()
        
        # Remove version numbers and common suffixes
        base_name = name_lower.replace(' v2', '').replace(' v3', '').replace(' v4', '')
        base_name = base_name.replace(' finance', '').replace(' protocol', '')
        
        variations.extend([
            base_name,
            base_name.replace(' ', ''),  # Remove spaces
            base_name.replace(' ', '-'), # Hyphenated
            name_lower.replace(' ', ''),  # Original without spaces
            name_lower.replace(' ', '-')  # Original hyphenated
        ])
        
        # Add specific mappings
        specific_mappings = {
            'aave': ['aave v3', 'aave v2', 'aave-v3', 'aave-v2'],
            'uniswap': ['uniswap v3', 'uniswap v4', 'uni', 'univ3', 'univ4'],
            'compound': ['comp', 'compound v3'],
            'makerdao': ['maker', 'dai', 'mkr'],
            'yearn': ['yearn finance', 'yfv'],
            'curve': ['curve finance', 'crv'],
            'lido': ['steth', 'wsteth'],
            'rocket pool': ['rocketpool', 'rpl', 'reth'],
            'convex': ['cvx'],
            'frax': ['frax finance', 'fxs']
        }
        
        for key, mappings in specific_mappings.items():
            if key in name_lower:
                variations.extend(mappings)
        
        return list(set(variations))  # Remove duplicates
    
    def is_supported(self, protocol_name: str) -> bool:
        """Check if protocol is in supported list"""
        if not protocol_name:
            return False
        
        normalized = self.normalize_name(protocol_name)
        return normalized is not None
    
    def normalize_name(self, protocol_name: str) -> Optional[str]:
        """Normalize protocol name to match supported list"""
        if not protocol_name:
            return None
            
        # Try exact match first
        clean_name = protocol_name.strip()
        if clean_name in self.supported_protocols:
            return clean_name
        
        # Try fuzzy matching
        lookup_key = clean_name.lower().strip()
        if lookup_key in self.protocol_mapping:
            return self.protocol_mapping[lookup_key]
        
        # Try partial matching
        for supported in self.supported_protocols:
            if (lookup_key in supported.lower() or 
                supported.lower() in lookup_key):
                return supported
        
        return None
    
    def get_all_protocols(self) -> List[str]:
        """Get list of all supported protocols"""
        return self.supported_protocols.copy()
    
    def get_protocol_info(self, protocol_name: str) -> Dict[str, any]:
        """Get detailed protocol information"""
        normalized = self.normalize_name(protocol_name)
        
        if not normalized:
            return {
                "supported": False,
                "normalized_name": None,
                "suggestions": self._get_suggestions(protocol_name)
            }
        
        return {
            "supported": True,
            "normalized_name": normalized,
            "original_input": protocol_name,
            "suggestions": []
        }
    
    def _get_suggestions(self, protocol_name: str, limit: int = 3) -> List[str]:
        """Get suggestions for unsupported protocol names"""
        if not protocol_name:
            return []
        
        suggestions = []
        input_lower = protocol_name.lower()
        
        # Find protocols that contain the input or vice versa
        for protocol in self.supported_protocols:
            protocol_lower = protocol.lower()
            if (input_lower in protocol_lower or 
                protocol_lower in input_lower or
                self._similar_words(input_lower, protocol_lower)):
                suggestions.append(protocol)
        
        return suggestions[:limit]
    
    def _similar_words(self, word1: str, word2: str) -> bool:
        """Check if two words are similar (basic implementation)"""
        # Simple similarity check
        if len(word1) < 3 or len(word2) < 3:
            return False
        
        # Check if they share common substrings
        for i in range(len(word1) - 2):
            substring = word1[i:i+3]
            if substring in word2:
                return True
        
        return False

# Global instance for easy importing
protocol_validator = ProtocolValidator()