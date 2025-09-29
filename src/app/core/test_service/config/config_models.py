"""
Configuration Models - Pydantic models for type-safe configuration.
"""

from typing import Dict, List, Optional
from pathlib import Path
from pydantic import BaseModel, Field


class LanguageConfig(BaseModel):
    """Configuration for a specific programming language."""
    
    # Compiler/Interpreter settings
    compiler: str = Field(..., description="Compiler executable")
    standard: str = Field(..., description="Language standard")
    optimization: str = Field(default="O2", description="Optimization level")
    
    # Flags and options
    architecture_flags: List[str] = Field(default_factory=list)
    debug_flags: List[str] = Field(default_factory=list) 
    extra_flags: List[str] = Field(default_factory=list)
    
    # Execution settings
    timeout: int = Field(default=30, description="Compilation timeout")
    memory_limit: Optional[int] = Field(default=None)


class ExecutionConfig(BaseModel):
    """Execution-related configuration."""
    
    max_parallel_workers: int = Field(default=4)
    default_test_timeout: int = Field(default=10)
    default_memory_limit: int = Field(default=256)


class TestServiceConfig(BaseModel):
    """Complete test service configuration."""
    
    # Language configurations
    languages: Dict[str, LanguageConfig] = Field(default_factory=dict)
    
    # Execution settings
    execution: ExecutionConfig = Field(default_factory=ExecutionConfig)
    
    # Resource management
    workspace_dir: Path = Field(...)
    cache_enabled: bool = Field(default=True)
    cleanup_temp_files: bool = Field(default=True)