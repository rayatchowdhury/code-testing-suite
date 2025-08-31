"""
Unit tests for Dependency Injection Container

Tests the DI container functionality
"""
import pytest
from app.dependency_injection import Container, get_container
from unittest.mock import Mock

class TestContainer:
    """Test dependency injection container"""
    
    def test_register_and_get_singleton(self):
        """Test singleton registration and retrieval"""
        container = Container()
        
        class TestService:
            def __init__(self):
                self.value = "test"
        
        class ITestService:
            pass
        
        container.register_singleton(ITestService, TestService)
        
        # Get service twice
        service1 = container.get(ITestService)
        service2 = container.get(ITestService)
        
        # Should be same instance
        assert service1 is service2
        assert service1.value == "test"
    
    def test_register_instance(self):
        """Test instance registration"""
        container = Container()
        
        class ITestService:
            pass
        
        test_instance = Mock()
        container.register_instance(ITestService, test_instance)
        
        retrieved = container.get(ITestService)
        assert retrieved is test_instance
    
    def test_register_factory(self):
        """Test factory registration"""
        container = Container()
        
        class ITestService:
            pass
        
        def create_service():
            service = Mock()
            service.created_by_factory = True
            return service
        
        container.register_factory(ITestService, create_service)
        
        service = container.get(ITestService)
        assert service.created_by_factory is True
    
    def test_service_not_registered(self):
        """Test error when service not registered"""
        container = Container()
        
        class IUnknownService:
            pass
        
        with pytest.raises(ValueError, match="not registered"):
            container.get(IUnknownService)
    
    def test_clear_container(self):
        """Test clearing container"""
        container = Container()
        
        class ITestService:
            pass
        
        container.register_instance(ITestService, Mock())
        assert len(container._singletons) > 0
        
        container.clear()
        assert len(container._singletons) == 0
        assert len(container._services) == 0
        assert len(container._factories) == 0
    
    def test_global_container(self):
        """Test global container access"""
        container1 = get_container()
        container2 = get_container()
        
        # Should return same instance
        assert container1 is container2
