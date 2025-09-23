"""
Tests for LLM Factory and multi-provider support.
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.services.llm_factory import LLMFactory
from src.services.llm_interface import LLMProvider
from src.services.azure_openai_service import AzureOpenAIService
from src.services.openai_service import OpenAIService
from src.services.anthropic_service import AnthropicService


class TestLLMFactory:
    """Test cases for LLM Factory."""

    def setup_method(self):
        """Reset factory before each test."""
        LLMFactory.reset()

    @pytest.mark.asyncio
    async def test_auto_detect_azure_openai(self):
        """Test auto-detection of Azure OpenAI when configured."""
        with patch('src.services.llm_factory.settings') as mock_settings:
            mock_settings.llm_provider = None
            mock_settings.azure_openai_endpoint = "https://test.openai.azure.com/"
            mock_settings.azure_openai_api_key = "test-key"
            mock_settings.openai_api_key = None
            mock_settings.anthropic_api_key = None
            
            with patch('src.services.azure_openai_service.AzureOpenAI'):
                service = LLMFactory.get_llm_service()
                
                assert isinstance(service, AzureOpenAIService)
                assert service.get_provider_name() == "Azure OpenAI"

    @pytest.mark.asyncio
    async def test_auto_detect_openai(self):
        """Test auto-detection of OpenAI when Azure OpenAI is not configured."""
        with patch('src.services.llm_factory.settings') as mock_settings:
            mock_settings.llm_provider = None
            mock_settings.azure_openai_endpoint = None
            mock_settings.azure_openai_api_key = None
            mock_settings.openai_api_key = "test-key"
            mock_settings.anthropic_api_key = None
            
            with patch('src.services.openai_service.OpenAI'):
                service = LLMFactory.get_llm_service()
                
                assert isinstance(service, OpenAIService)
                assert service.get_provider_name() == "OpenAI ChatGPT"

    @pytest.mark.asyncio
    async def test_auto_detect_anthropic(self):
        """Test auto-detection of Anthropic when others are not configured."""
        with patch('src.services.llm_factory.settings') as mock_settings:
            mock_settings.llm_provider = None
            mock_settings.azure_openai_endpoint = None
            mock_settings.azure_openai_api_key = None
            mock_settings.openai_api_key = None
            mock_settings.anthropic_api_key = "test-key"
            
            with patch('src.services.anthropic_service.anthropic.Anthropic'):
                service = LLMFactory.get_llm_service()
                
                assert isinstance(service, AnthropicService)
                assert service.get_provider_name() == "Anthropic Claude"

    def test_explicit_provider_selection(self):
        """Test explicit provider selection via configuration."""
        with patch('src.services.llm_factory.settings') as mock_settings:
            mock_settings.llm_provider = "openai"
            mock_settings.openai_api_key = "test-key"
            
            with patch('src.services.openai_service.OpenAI'):
                service = LLMFactory.get_llm_service()
                
                assert isinstance(service, OpenAIService)

    def test_unsupported_provider(self):
        """Test error when unsupported provider is specified."""
        with patch('src.services.llm_factory.settings') as mock_settings:
            mock_settings.llm_provider = "unsupported_provider"
            
            with pytest.raises(ValueError, match="Unsupported LLM provider"):
                LLMFactory.get_llm_service()

    def test_no_provider_configured(self):
        """Test error when no provider is configured."""
        with patch('src.services.llm_factory.settings') as mock_settings:
            mock_settings.llm_provider = None
            mock_settings.azure_openai_endpoint = None
            mock_settings.azure_openai_api_key = None
            mock_settings.openai_api_key = None
            mock_settings.anthropic_api_key = None
            
            with pytest.raises(RuntimeError, match="No LLM provider is configured"):
                LLMFactory.get_llm_service()

    def test_list_available_providers(self):
        """Test listing available providers and their status."""
        with patch('src.services.azure_openai_service.settings') as mock_azure_settings:
            mock_azure_settings.azure_openai_endpoint = "https://test.openai.azure.com/"
            mock_azure_settings.azure_openai_api_key = "test-key"
            
            with patch('src.services.openai_service.settings') as mock_openai_settings:
                mock_openai_settings.openai_api_key = None
                
                with patch('src.services.anthropic_service.settings') as mock_anthropic_settings:
                    mock_anthropic_settings.anthropic_api_key = None
                    
                    with patch('src.services.azure_openai_service.AzureOpenAI'):
                        status = LLMFactory.list_available_providers()
                        
                        assert "azure_openai" in status
                        assert "openai" in status
                        assert "anthropic" in status
                        assert status["azure_openai"] is True
                        assert status["openai"] is False
                        assert status["anthropic"] is False

    def test_singleton_behavior(self):
        """Test that factory returns the same instance on subsequent calls."""
        with patch('src.services.llm_factory.settings') as mock_settings:
            mock_settings.llm_provider = "azure_openai"
            mock_settings.azure_openai_endpoint = "https://test.openai.azure.com/"
            mock_settings.azure_openai_api_key = "test-key"
            
            with patch('src.services.azure_openai_service.AzureOpenAI'):
                service1 = LLMFactory.get_llm_service()
                service2 = LLMFactory.get_llm_service()
                
                assert service1 is service2


class TestMultiProviderIntegration:
    """Test cases for multi-provider integration."""

    @pytest.mark.asyncio
    async def test_azure_openai_parameters(self):
        """Test Azure OpenAI with custom parameters."""
        with patch('src.services.azure_openai_service.settings') as mock_settings:
            mock_settings.azure_openai_endpoint = "https://test.openai.azure.com/"
            mock_settings.azure_openai_api_key = "test-key"
            mock_settings.azure_openai_deployment_name = "gpt-4"
            
            mock_client = Mock()
            
            # Create nested mock structure for OpenAI response
            mock_message = Mock()
            mock_message.content = "Test response"
            mock_choice = Mock()
            mock_choice.message = mock_message
            mock_response = Mock()
            mock_response.choices = [mock_choice]
            
            mock_client.chat.completions.create.return_value = mock_response
            
            with patch('src.services.azure_openai_service.AzureOpenAI', return_value=mock_client):
                service = AzureOpenAIService()
                
                response = await service.ask_llm("Test question", max_tokens=500, temperature=0.5)
                
                assert response == "Test response"
                mock_client.chat.completions.create.assert_called_once()
                call_args = mock_client.chat.completions.create.call_args[1]
                assert call_args["max_tokens"] == 500
                assert call_args["temperature"] == 0.5

    @pytest.mark.asyncio
    async def test_openai_parameters(self):
        """Test OpenAI with custom parameters."""
        with patch('src.services.openai_service.settings') as mock_settings:
            mock_settings.openai_api_key = "test-key"
            mock_settings.openai_model_name = "gpt-4"
            
            mock_client = Mock()
            
            # Create nested mock structure for OpenAI response
            mock_message = Mock()
            mock_message.content = "Test response"
            mock_choice = Mock()
            mock_choice.message = mock_message
            mock_response = Mock()
            mock_response.choices = [mock_choice]
            
            mock_client.chat.completions.create.return_value = mock_response
            
            with patch('src.services.openai_service.OpenAI', return_value=mock_client):
                service = OpenAIService()
                
                response = await service.ask_llm("Test question", max_tokens=800)
                
                assert response == "Test response"
                mock_client.chat.completions.create.assert_called_once()
                call_args = mock_client.chat.completions.create.call_args[1]
                assert call_args["max_tokens"] == 800

    @pytest.mark.asyncio
    async def test_anthropic_parameters(self):
        """Test Anthropic with custom parameters."""
        with patch('src.services.anthropic_service.settings') as mock_settings:
            mock_settings.anthropic_api_key = "test-key"
            mock_settings.anthropic_model_name = "claude-3-sonnet-20240229"
            
            mock_client = Mock()
            
            # Create nested mock structure for Anthropic response
            mock_content_item = Mock()
            mock_content_item.text = "Test response"
            mock_response = Mock()
            mock_response.content = [mock_content_item]
            
            mock_client.messages.create.return_value = mock_response
            
            with patch('src.services.anthropic_service.anthropic.Anthropic', return_value=mock_client):
                service = AnthropicService()
                
                response = await service.ask_llm("Test question", max_tokens=1200, temperature=0.9)
                
                assert response == "Test response"
                mock_client.messages.create.assert_called_once()
                call_args = mock_client.messages.create.call_args[1]
                assert call_args["max_tokens"] == 1200
                assert call_args["temperature"] == 0.9
