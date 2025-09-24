"""
Azure API Client for AZEBAL

Comprehensive Azure API client for debugging operations and resource analysis.
"""

import re
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
import httpx

from src.core.logging_config import get_logger

logger = get_logger(__name__)


class AzureAPIClient:
    """Comprehensive Azure API client for debugging operations."""
    
    def __init__(self, access_token: str, subscription_id: Optional[str] = None):
        """
        Initialize Azure API client.
        
        Args:
            access_token: Azure access token for authentication
            subscription_id: Optional Azure subscription ID
        """
        self.access_token = access_token
        self.subscription_id = subscription_id
        self.base_url = "https://management.azure.com"
        self.timeout = httpx.Timeout(30.0)
        
        # Headers for all requests
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        logger.info(f"AzureAPIClient initialized for subscription: {subscription_id}")
    
    async def get_subscriptions(self) -> Dict[str, Any]:
        """Get list of available subscriptions."""
        url = f"{self.base_url}/subscriptions?api-version=2021-04-01"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    subscriptions = data.get("value", [])
                    
                    logger.info(f"Found {len(subscriptions)} subscriptions")
                    return {
                        "success": True,
                        "subscriptions": subscriptions,
                        "count": len(subscriptions)
                    }
                else:
                    logger.error(f"Failed to get subscriptions: {response.status_code} - {response.text}")
                    return {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "message": response.text
                    }
                    
        except Exception as e:
            logger.error(f"Error getting subscriptions: {str(e)}")
            return {
                "success": False,
                "error": "REQUEST_FAILED",
                "message": str(e)
            }
    
    async def get_resource_status(self, resource_id: str) -> Dict[str, Any]:
        """
        Get comprehensive status of any Azure resource.
        
        Args:
            resource_id: Full Azure resource ID
            
        Returns:
            Dict containing resource status and information
        """
        try:
            # Parse resource ID
            parsed = self._parse_resource_id(resource_id)
            if not parsed:
                return {
                    "success": False,
                    "error": "INVALID_RESOURCE_ID",
                    "message": "Invalid Azure resource ID format"
                }
            
            resource_type = f"{parsed['provider']}/{parsed['resource_type']}"
            logger.info(f"Getting status for resource type: {resource_type}")
            
            # Route to appropriate handler
            handlers = {
                "Microsoft.Compute/virtualMachines": self._get_vm_status,
                "Microsoft.Storage/storageAccounts": self._get_storage_status,
                "Microsoft.Web/sites": self._get_app_service_status,
                "Microsoft.ContainerInstance/containerGroups": self._get_container_status,
                "Microsoft.Network/applicationGateways": self._get_app_gateway_status,
                "Microsoft.Network/loadBalancers": self._get_load_balancer_status,
                "Microsoft.Sql/servers": self._get_sql_server_status,
                "Microsoft.DBforPostgreSQL/servers": self._get_postgresql_status,
            }
            
            handler = handlers.get(resource_type, self._get_generic_resource_status)
            return await handler(resource_id, parsed)
            
        except Exception as e:
            logger.error(f"Error getting resource status for {resource_id}: {str(e)}")
            return {
                "success": False,
                "error": "RESOURCE_STATUS_FAILED",
                "resource_id": resource_id,
                "message": str(e),
                "recommendation": "Check resource ID format and permissions"
            }
    
    async def query_resource_logs(
        self, 
        resource_id: str, 
        time_range: str = "1h",
        query: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query Azure Monitor logs for a resource.
        
        Args:
            resource_id: Azure resource ID
            time_range: Time range like '1h', '24h', '7d'
            query: Optional KQL query
            
        Returns:
            Dict containing log query results
        """
        try:
            # Build KQL query based on resource type and time range
            if not query:
                query = self._build_default_log_query(resource_id, time_range)
            
            logger.info(f"Querying logs for resource: {resource_id}, time_range: {time_range}")
            
            # Note: This is a simplified implementation
            # Full implementation would use Azure Monitor Query API
            return {
                "success": True,
                "resource_id": resource_id,
                "time_range": time_range,
                "query": query,
                "note": "Log querying implementation pending - requires Azure Monitor Query API setup",
                "recommendations": [
                    "Check Azure Monitor logs in portal",
                    "Review application insights data",
                    "Check for error patterns in recent logs"
                ]
            }
            
        except Exception as e:
            logger.error(f"Error querying logs for {resource_id}: {str(e)}")
            return {
                "success": False,
                "error": "LOG_QUERY_FAILED",
                "resource_id": resource_id,
                "message": str(e),
                "recommendation": "Verify Monitor access permissions and resource configuration"
            }
    
    async def check_resource_permissions(self, resource_id: str) -> Dict[str, Any]:
        """
        Check user permissions on a specific resource.
        
        Args:
            resource_id: Azure resource ID
            
        Returns:
            Dict containing permission information
        """
        try:
            # Check if we can read the resource (basic permission check)
            url = f"{self.base_url}{resource_id}?api-version=2021-04-01"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    return {
                        "success": True,
                        "resource_id": resource_id,
                        "permissions": ["read"],
                        "message": "User has read access to the resource"
                    }
                elif response.status_code == 403:
                    return {
                        "success": False,
                        "resource_id": resource_id,
                        "error": "INSUFFICIENT_PERMISSIONS",
                        "message": "User does not have permission to access this resource",
                        "recommendations": [
                            "Check Azure RBAC role assignments",
                            "Verify user has required permissions",
                            "Contact Azure administrator for access"
                        ]
                    }
                elif response.status_code == 404:
                    return {
                        "success": False,
                        "resource_id": resource_id,
                        "error": "RESOURCE_NOT_FOUND",
                        "message": "Resource does not exist or is not accessible",
                        "recommendations": [
                            "Verify resource ID format",
                            "Check if resource exists in the subscription",
                            "Ensure correct subscription and resource group"
                        ]
                    }
                else:
                    return {
                        "success": False,
                        "resource_id": resource_id,
                        "error": f"HTTP_{response.status_code}",
                        "message": f"Unexpected response: {response.status_code}"
                    }
                    
        except Exception as e:
            logger.error(f"Error checking permissions for {resource_id}: {str(e)}")
            return {
                "success": False,
                "error": "PERMISSION_CHECK_FAILED",
                "resource_id": resource_id,
                "message": str(e)
            }
    
    async def get_resource_group_resources(self, resource_group: str) -> Dict[str, Any]:
        """
        Get all resources in a resource group.
        
        Args:
            resource_group: Resource group name
            
        Returns:
            Dict containing resource list
        """
        if not self.subscription_id:
            return {
                "success": False,
                "error": "NO_SUBSCRIPTION",
                "message": "Subscription ID is required"
            }
        
        url = f"{self.base_url}/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/resources?api-version=2021-04-01"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    data = response.json()
                    resources = data.get("value", [])
                    
                    logger.info(f"Found {len(resources)} resources in resource group: {resource_group}")
                    return {
                        "success": True,
                        "resource_group": resource_group,
                        "resources": resources,
                        "count": len(resources)
                    }
                else:
                    logger.error(f"Failed to get resources for RG {resource_group}: {response.status_code}")
                    return {
                        "success": False,
                        "error": f"HTTP_{response.status_code}",
                        "message": response.text
                    }
                    
        except Exception as e:
            logger.error(f"Error getting resources for RG {resource_group}: {str(e)}")
            return {
                "success": False,
                "error": "REQUEST_FAILED",
                "message": str(e)
            }
    
    def _parse_resource_id(self, resource_id: str) -> Optional[Dict[str, str]]:
        """Parse Azure resource ID into components."""
        if not resource_id:
            return None
        
        # Azure resource ID pattern:
        # /subscriptions/{subscription}/resourceGroups/{rg}/providers/{provider}/{type}/{name}
        pattern = r'^/subscriptions/([^/]+)/resourceGroups/([^/]+)/providers/([^/]+)/([^/]+)/([^/]+)(?:/(.+))?$'
        match = re.match(pattern, resource_id)
        
        if not match:
            logger.warning(f"Invalid Azure resource ID format: {resource_id}")
            return None
        
        return {
            "subscription_id": match.group(1),
            "resource_group": match.group(2),
            "provider": match.group(3),
            "resource_type": match.group(4),
            "resource_name": match.group(5),
            "sub_resource": match.group(6) if match.group(6) else None
        }
    
    async def _get_vm_status(self, resource_id: str, parsed: Dict[str, str]) -> Dict[str, Any]:
        """Get VM-specific status information."""
        # Get VM with instance view
        url = f"{self.base_url}{resource_id}?api-version=2021-11-01&$expand=instanceView"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    vm_data = response.json()
                    instance_view = vm_data.get("properties", {}).get("instanceView", {})
                    
                    # Extract status information
                    statuses = instance_view.get("statuses", [])
                    power_state = "Unknown"
                    provisioning_state = vm_data.get("properties", {}).get("provisioningState", "Unknown")
                    
                    for status in statuses:
                        if "PowerState" in status.get("code", ""):
                            power_state = status.get("displayStatus", "Unknown")
                            break
                    
                    return {
                        "success": True,
                        "resource_type": "Virtual Machine",
                        "name": vm_data.get("name"),
                        "location": vm_data.get("location"),
                        "provisioning_state": provisioning_state,
                        "power_state": power_state,
                        "vm_size": vm_data.get("properties", {}).get("hardwareProfile", {}).get("vmSize"),
                        "os_type": vm_data.get("properties", {}).get("storageProfile", {}).get("osDisk", {}).get("osType"),
                        "statuses": statuses,
                        "recommendations": self._get_vm_recommendations(vm_data)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP_{response.status_code}",
                        "message": f"Failed to get VM status: {response.text}"
                    }
                    
        except Exception as e:
            logger.error(f"Error getting VM status: {str(e)}")
            return {
                "success": False,
                "error": "VM_STATUS_FAILED",
                "message": str(e)
            }
    
    async def _get_storage_status(self, resource_id: str, parsed: Dict[str, str]) -> Dict[str, Any]:
        """Get Storage Account status."""
        url = f"{self.base_url}{resource_id}?api-version=2021-08-01"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    storage_data = response.json()
                    properties = storage_data.get("properties", {})
                    
                    return {
                        "success": True,
                        "resource_type": "Storage Account",
                        "name": storage_data.get("name"),
                        "location": storage_data.get("location"),
                        "provisioning_state": properties.get("provisioningState"),
                        "primary_location": properties.get("primaryLocation"),
                        "status_of_primary": properties.get("statusOfPrimary"),
                        "access_tier": properties.get("accessTier"),
                        "kind": storage_data.get("kind"),
                        "sku": storage_data.get("sku", {}),
                        "recommendations": self._get_storage_recommendations(storage_data)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP_{response.status_code}",
                        "message": f"Failed to get storage status: {response.text}"
                    }
                    
        except Exception as e:
            logger.error(f"Error getting storage status: {str(e)}")
            return {
                "success": False,
                "error": "STORAGE_STATUS_FAILED",
                "message": str(e)
            }
    
    async def _get_app_service_status(self, resource_id: str, parsed: Dict[str, str]) -> Dict[str, Any]:
        """Get App Service status."""
        url = f"{self.base_url}{resource_id}?api-version=2021-02-01"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    app_data = response.json()
                    properties = app_data.get("properties", {})
                    
                    return {
                        "success": True,
                        "resource_type": "App Service",
                        "name": app_data.get("name"),
                        "location": app_data.get("location"),
                        "state": properties.get("state"),
                        "enabled": properties.get("enabled"),
                        "default_host_name": properties.get("defaultHostName"),
                        "runtime_version": properties.get("siteConfig", {}).get("linuxFxVersion") or properties.get("siteConfig", {}).get("netFrameworkVersion"),
                        "app_service_plan_id": properties.get("serverFarmId"),
                        "recommendations": self._get_app_service_recommendations(app_data)
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP_{response.status_code}",
                        "message": f"Failed to get app service status: {response.text}"
                    }
                    
        except Exception as e:
            logger.error(f"Error getting app service status: {str(e)}")
            return {
                "success": False,
                "error": "APP_SERVICE_STATUS_FAILED",
                "message": str(e)
            }
    
    async def _get_generic_resource_status(self, resource_id: str, parsed: Dict[str, str]) -> Dict[str, Any]:
        """Get generic resource status for unsupported resource types."""
        url = f"{self.base_url}{resource_id}?api-version=2021-04-01"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=self.headers)
                
                if response.status_code == 200:
                    resource_data = response.json()
                    
                    return {
                        "success": True,
                        "resource_type": f"{parsed['provider']}/{parsed['resource_type']}",
                        "name": resource_data.get("name"),
                        "location": resource_data.get("location"),
                        "kind": resource_data.get("kind"),
                        "properties": resource_data.get("properties", {}),
                        "tags": resource_data.get("tags", {}),
                        "note": "Generic resource status - specific debugging methods not implemented",
                        "recommendations": [
                            "Check resource in Azure portal for detailed status",
                            "Review resource-specific logs and metrics",
                            "Verify resource configuration"
                        ]
                    }
                else:
                    return {
                        "success": False,
                        "error": f"HTTP_{response.status_code}",
                        "message": f"Failed to get resource status: {response.text}"
                    }
                    
        except Exception as e:
            logger.error(f"Error getting generic resource status: {str(e)}")
            return {
                "success": False,
                "error": "GENERIC_STATUS_FAILED",
                "message": str(e)
            }
    
    # Placeholder methods for other resource types
    async def _get_container_status(self, resource_id: str, parsed: Dict[str, str]) -> Dict[str, Any]:
        """Get Container Instance status."""
        return await self._get_generic_resource_status(resource_id, parsed)
    
    async def _get_app_gateway_status(self, resource_id: str, parsed: Dict[str, str]) -> Dict[str, Any]:
        """Get Application Gateway status."""
        return await self._get_generic_resource_status(resource_id, parsed)
    
    async def _get_load_balancer_status(self, resource_id: str, parsed: Dict[str, str]) -> Dict[str, Any]:
        """Get Load Balancer status."""
        return await self._get_generic_resource_status(resource_id, parsed)
    
    async def _get_sql_server_status(self, resource_id: str, parsed: Dict[str, str]) -> Dict[str, Any]:
        """Get SQL Server status."""
        return await self._get_generic_resource_status(resource_id, parsed)
    
    async def _get_postgresql_status(self, resource_id: str, parsed: Dict[str, str]) -> Dict[str, Any]:
        """Get PostgreSQL status."""
        return await self._get_generic_resource_status(resource_id, parsed)
    
    def _build_default_log_query(self, resource_id: str, time_range: str) -> str:
        """Build default KQL query for resource logs."""
        # Convert time range to TimeSpan format
        time_span_map = {
            "1h": "1h",
            "6h": "6h", 
            "12h": "12h",
            "24h": "1d",
            "7d": "7d",
            "30d": "30d"
        }
        
        time_span = time_span_map.get(time_range, "1h")
        
        # Basic KQL query template
        query = f"""
        // Default log query for resource: {resource_id}
        // Time range: {time_range}
        union isfuzzy=true
            AppTraces,
            AppExceptions,
            AppRequests,
            AppDependencies
        | where TimeGenerated >= ago({time_span})
        | where ResourceId contains "{resource_id}" or ResourceId == "{resource_id}"
        | order by TimeGenerated desc
        | limit 100
        """
        
        return query.strip()
    
    def _get_vm_recommendations(self, vm_data: Dict[str, Any]) -> List[str]:
        """Get VM-specific recommendations."""
        recommendations = []
        
        properties = vm_data.get("properties", {})
        instance_view = properties.get("instanceView", {})
        
        # Check VM status
        statuses = instance_view.get("statuses", [])
        for status in statuses:
            if "PowerState" in status.get("code", ""):
                if "deallocated" in status.get("code", "").lower():
                    recommendations.append("VM is deallocated - start the VM to resolve issues")
                elif "stopped" in status.get("code", "").lower():
                    recommendations.append("VM is stopped - check why it was stopped")
        
        # Check provisioning state
        prov_state = properties.get("provisioningState")
        if prov_state != "Succeeded":
            recommendations.append(f"VM provisioning state is {prov_state} - check deployment logs")
        
        # General recommendations
        recommendations.extend([
            "Check VM metrics in Azure Monitor",
            "Review VM diagnostic logs",
            "Verify network security group rules",
            "Check disk space and performance"
        ])
        
        return recommendations
    
    def _get_storage_recommendations(self, storage_data: Dict[str, Any]) -> List[str]:
        """Get Storage Account-specific recommendations."""
        recommendations = []
        
        properties = storage_data.get("properties", {})
        
        # Check status
        status = properties.get("statusOfPrimary")
        if status != "available":
            recommendations.append(f"Storage account primary location status: {status}")
        
        # Check provisioning state
        prov_state = properties.get("provisioningState")
        if prov_state != "Succeeded":
            recommendations.append(f"Storage provisioning state is {prov_state}")
        
        # General recommendations
        recommendations.extend([
            "Check storage account metrics and alerts",
            "Verify access keys and connection strings",
            "Review storage account firewall rules",
            "Check for throttling issues"
        ])
        
        return recommendations
    
    def _get_app_service_recommendations(self, app_data: Dict[str, Any]) -> List[str]:
        """Get App Service-specific recommendations."""
        recommendations = []
        
        properties = app_data.get("properties", {})
        
        # Check app state
        state = properties.get("state")
        if state != "Running":
            recommendations.append(f"App Service state is {state} - check why it's not running")
        
        # Check enabled status
        if not properties.get("enabled", True):
            recommendations.append("App Service is disabled - enable it to resolve issues")
        
        # General recommendations
        recommendations.extend([
            "Check App Service logs",
            "Review application insights data",
            "Verify app settings and connection strings",
            "Check App Service Plan capacity and scaling"
        ])
        
        return recommendations


class AzureAPIErrorHandler:
    """Handle Azure API errors with actionable suggestions."""
    
    @staticmethod
    def handle_azure_api_error(error: Exception, operation: str, resource_id: str = None) -> Dict[str, Any]:
        """Handle Azure API errors with actionable suggestions."""
        
        error_mappings = {
            "AuthenticationFailed": {
                "message": "Azure authentication failed",
                "suggestions": [
                    "Verify Azure CLI login status: az account show",
                    "Check token expiration: az account get-access-token",
                    "Ensure proper subscription access"
                ],
                "retry": False
            },
            "ResourceNotFound": {
                "message": "Azure resource not found",
                "suggestions": [
                    "Verify resource ID format",
                    "Check if resource exists in the subscription",
                    "Ensure proper resource group and subscription"
                ],
                "retry": False
            },
            "InsufficientPermissions": {
                "message": "Insufficient permissions for operation",
                "suggestions": [
                    "Check Azure RBAC role assignments",
                    "Verify user has required permissions",
                    "Contact Azure administrator for access"
                ],
                "retry": False
            },
            "ThrottlingError": {
                "message": "Azure API rate limit exceeded",
                "suggestions": [
                    "Wait before retrying the operation",
                    "Reduce API call frequency",
                    "Consider upgrading service tier"
                ],
                "retry": True,
                "retry_after": 60
            },
            "ServiceUnavailable": {
                "message": "Azure service temporarily unavailable",
                "suggestions": [
                    "Check Azure service health status",
                    "Retry operation after delay",
                    "Monitor Azure status page"
                ],
                "retry": True,
                "retry_after": 30
            }
        }
        
        error_type = type(error).__name__
        error_str = str(error)
        
        # Check for specific error patterns in the error message
        if "401" in error_str or "Unauthorized" in error_str:
            error_type = "AuthenticationFailed"
        elif "403" in error_str or "Forbidden" in error_str:
            error_type = "InsufficientPermissions"
        elif "404" in error_str or "Not Found" in error_str:
            error_type = "ResourceNotFound"
        elif "429" in error_str or "throttl" in error_str.lower():
            error_type = "ThrottlingError"
        elif "503" in error_str or "Service Unavailable" in error_str:
            error_type = "ServiceUnavailable"
        
        error_info = error_mappings.get(error_type, {
            "message": f"Unexpected error: {error_str}",
            "suggestions": ["Review error details and contact support if needed"],
            "retry": False
        })
        
        return {
            "operation": operation,
            "resource_id": resource_id,
            "error_type": error_type,
            "error_message": error_info["message"],
            "suggestions": error_info["suggestions"],
            "can_retry": error_info.get("retry", False),
            "retry_after": error_info.get("retry_after", 0),
            "raw_error": error_str
        }
