# TODO: Create dependency injection container for v2 architecture
"""
Dependency Injection Container

Simple dependency injection container to wire services and break circular dependencies.
Based on the dependency injection pattern from the refactoring plan.
"""
from typing import TypeVar, Type, Dict, Any, Callable, Protocol
from abc import ABC, abstractmethod

T = TypeVar('T')

class Container:
    """
    Simple dependency injection container.
    
    ASSUMPTION: Provides basic DI capabilities without external dependencies.
    Supports singleton and transient lifetimes.
    """
    
    def __init__(self):
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable] = {}
        self._singletons: Dict[Type, Any] = {}
    
    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a service as singleton (one instance per container)"""
        self._services[interface] = implementation
    
    def register_transient(self, interface: Type[T], implementation: Type[T]) -> None:
        """Register a service as transient (new instance each time)"""
        self._services[interface] = implementation
    
    def register_factory(self, interface: Type[T], factory: Callable[[], T]) -> None:
        """Register a factory function for a service"""
        self._factories[interface] = factory
    
    def register_instance(self, interface: Type[T], instance: T) -> None:
        """Register a specific instance"""
        self._singletons[interface] = instance
    
    def get(self, interface: Type[T]) -> T:
        """Get an instance of the requested service"""
        # Check for registered instance first
        if interface in self._singletons:
            return self._singletons[interface]
        
        # Check for factory
        if interface in self._factories:
            return self._factories[interface]()
        
        # Check for registered service
        if interface in self._services:
            implementation = self._services[interface]
            
            # Create instance
            instance = implementation()
            
            # Cache as singleton if this was registered as singleton
            self._singletons[interface] = instance
            return instance
        
        raise ValueError(f"Service {interface.__name__} not registered")
    
    def clear(self) -> None:
        """Clear all registrations (useful for testing)"""
        self._services.clear()
        self._factories.clear()
        self._singletons.clear()

# Global container instance
_container = Container()

def get_container() -> Container:
    """Get the global dependency injection container"""
    return _container

def register_services():
    """
    Register all v2 services in the container.
    
    TODO: This will be called during application startup to wire all dependencies.
    """
    from domain.services.compilation_service import CompilationService
    from infrastructure.compilation.compiler_service import BasicCompilationService
    from infrastructure.configuration.config_service import ConfigService
    from infrastructure.file_system.file_service import FileService
    
    container = get_container()
    
    # Register infrastructure services
    container.register_singleton(ConfigService, ConfigService)
    container.register_singleton(FileService, FileService)
    container.register_singleton(CompilationService, BasicCompilationService)
    
    print("✅ v2 services registered in DI container")
