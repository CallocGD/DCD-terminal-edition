from enum import IntFlag
from dataclasses import dataclass, field
from typing import Union 

class ObfuscationLevel(IntFlag):
    NONE = 0
    """Ignore all Obfucation Technqiues..."""
    GDBROWSER = 1    
    """Mask ourselves as a Gdbrowser instance"""
    XFAKEIP = 2
    """Generates a decoy unless one has been provided"""
    ALL = 3

def configure_flags(flag:Union[str,int]) -> ObfuscationLevel:
    if isinstance(flag,int):
        return ObfuscationLevel(flag)
    else:
        return ObfuscationLevel._member_map_[flag.upper()]




