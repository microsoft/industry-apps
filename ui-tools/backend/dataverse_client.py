"""
Dataverse Client for Field Creation and Management
Handles authentication and API calls to Dataverse Web API
"""

import json
import logging
from typing import Dict, List, Optional, Any
import httpx
from msal import ConfidentialClientApplication

logger = logging.getLogger(__name__)


class DataverseClient:
    """Client for interacting with Dataverse Web API"""
    
    # Dataverse API version
    API_VERSION = "v9.2"
    
    # Field type mappings from UI to Dataverse AttributeTypeCode
    FIELD_TYPE_MAP = {
        "Text": "String",
        "Number": "Integer",
        "Decimal": "Decimal",
        "Float": "Double",
        "Currency": "Money",
        "Date": "DateTime",
        "DateTime": "DateTime",
        "Boolean": "Boolean",
        "Choice": "Picklist",
        "MultiChoice": "MultiSelectPicklist",
        "Lookup": "Lookup",
        "Customer": "Customer",
        "Owner": "Owner"
    }
    
    def __init__(self, environment_url: str, tenant_id: str, client_id: str, client_secret: str):
        """
        Initialize Dataverse client
        
        Args:
            environment_url: Dataverse environment URL (e.g., https://org.crm.dynamics.com)
            tenant_id: Azure AD tenant ID
            client_id: Application (client) ID
            client_secret: Application client secret
        """
        self.environment_url = environment_url.rstrip('/')
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        
        # Initialize MSAL client
        self.authority = f"https://login.microsoftonline.com/{tenant_id}"
        self.app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=self.authority
        )
        
    def authenticate(self) -> str:
        """
        Authenticate and get access token
        
        Returns:
            Access token string
        """
        # Dataverse scope
        scopes = [f"{self.environment_url}/.default"]
        
        try:
            result = self.app.acquire_token_for_client(scopes=scopes)
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                logger.info("Successfully authenticated to Dataverse")
                return self.access_token
            else:
                error_msg = result.get("error_description", result.get("error", "Unknown error"))
                raise Exception(f"Authentication failed: {error_msg}")
                
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            raise
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authorization"""
        if not self.access_token:
            self.authenticate()
        
        return {
            "Authorization": f"Bearer {self.access_token}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8"
        }
    
    def create_string_field(
        self, 
        table_name: str, 
        schema_name: str, 
        display_name: str,
        max_length: int = 100,
        required: bool = False,
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a single-line text field"""
        
        attribute = {
            "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
            "AttributeType": "String",
            "AttributeTypeName": {
                "Value": "StringType"
            },
            "SchemaName": schema_name,
            "RequiredLevel": {
                "Value": "ApplicationRequired" if required else "None",
                "CanBeChanged": True
            },
            "DisplayName": {
                "@odata.type": "Microsoft.Dynamics.CRM.Label",
                "LocalizedLabels": [
                    {
                        "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                        "Label": display_name,
                        "LanguageCode": 1033
                    }
                ]
            },
            "Description": {
                "@odata.type": "Microsoft.Dynamics.CRM.Label",
                "LocalizedLabels": [
                    {
                        "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                        "Label": description,
                        "LanguageCode": 1033
                    }
                ]
            },
            "MaxLength": max_length,
            "FormatName": {
                "Value": "Text"
            }
        }
        
        return self._create_attribute(table_name, attribute)
    
    def create_integer_field(
        self,
        table_name: str,
        schema_name: str,
        display_name: str,
        required: bool = False,
        min_value: int = -2147483648,
        max_value: int = 2147483647,
        description: str = ""
    ) -> Dict[str, Any]:
        """Create an integer (whole number) field"""
        
        attribute = {
            "@odata.type": "Microsoft.Dynamics.CRM.IntegerAttributeMetadata",
            "AttributeType": "Integer",
            "AttributeTypeName": {
                "Value": "IntegerType"
            },
            "SchemaName": schema_name,
            "RequiredLevel": {
                "Value": "ApplicationRequired" if required else "None",
                "CanBeChanged": True
            },
            "DisplayName": {
                "@odata.type": "Microsoft.Dynamics.CRM.Label",
                "LocalizedLabels": [
                    {
                        "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                        "Label": display_name,
                        "LanguageCode": 1033
                    }
                ]
            },
            "Description": {
                "@odata.type": "Microsoft.Dynamics.CRM.Label",
                "LocalizedLabels": [
                    {
                        "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                        "Label": description,
                        "LanguageCode": 1033
                    }
                ]
            },
            "Format": "None",
            "MinValue": min_value,
            "MaxValue": max_value
        }
        
        return self._create_attribute(table_name, attribute)
    
    def create_boolean_field(
        self,
        table_name: str,
        schema_name: str,
        display_name: str,
        required: bool = False,
        default_value: bool = False,
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a yes/no (boolean) field"""
        
        attribute = {
            "@odata.type": "Microsoft.Dynamics.CRM.BooleanAttributeMetadata",
            "AttributeType": "Boolean",
            "AttributeTypeName": {
                "Value": "BooleanType"
            },
            "SchemaName": schema_name,
            "RequiredLevel": {
                "Value": "ApplicationRequired" if required else "None",
                "CanBeChanged": True
            },
            "DisplayName": {
                "@odata.type": "Microsoft.Dynamics.CRM.Label",
                "LocalizedLabels": [
                    {
                        "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                        "Label": display_name,
                        "LanguageCode": 1033
                    }
                ]
            },
            "Description": {
                "@odata.type": "Microsoft.Dynamics.CRM.Label",
                "LocalizedLabels": [
                    {
                        "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                        "Label": description,
                        "LanguageCode": 1033
                    }
                ]
            },
            "DefaultValue": default_value,
            "OptionSet": {
                "@odata.type": "Microsoft.Dynamics.CRM.BooleanOptionSetMetadata",
                "TrueOption": {
                    "Value": 1,
                    "Label": {
                        "@odata.type": "Microsoft.Dynamics.CRM.Label",
                        "LocalizedLabels": [
                            {
                                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                                "Label": "Yes",
                                "LanguageCode": 1033
                            }
                        ]
                    }
                },
                "FalseOption": {
                    "Value": 0,
                    "Label": {
                        "@odata.type": "Microsoft.Dynamics.CRM.Label",
                        "LocalizedLabels": [
                            {
                                "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                                "Label": "No",
                                "LanguageCode": 1033
                            }
                        ]
                    }
                }
            }
        }
        
        return self._create_attribute(table_name, attribute)
    
    def create_datetime_field(
        self,
        table_name: str,
        schema_name: str,
        display_name: str,
        required: bool = False,
        include_time: bool = True,
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a date/time field"""
        
        attribute = {
            "@odata.type": "Microsoft.Dynamics.CRM.DateTimeAttributeMetadata",
            "AttributeType": "DateTime",
            "AttributeTypeName": {
                "Value": "DateTimeType"
            },
            "SchemaName": schema_name,
            "RequiredLevel": {
                "Value": "ApplicationRequired" if required else "None",
                "CanBeChanged": True
            },
            "DisplayName": {
                "@odata.type": "Microsoft.Dynamics.CRM.Label",
                "LocalizedLabels": [
                    {
                        "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                        "Label": display_name,
                        "LanguageCode": 1033
                    }
                ]
            },
            "Description": {
                "@odata.type": "Microsoft.Dynamics.CRM.Label",
                "LocalizedLabels": [
                    {
                        "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                        "Label": description,
                        "LanguageCode": 1033
                    }
                ]
            },
            "Format": "DateAndTime" if include_time else "DateOnly"
        }
        
        return self._create_attribute(table_name, attribute)
    
    def _create_attribute(self, table_name: str, attribute: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create an attribute (field) on a table
        
        Args:
            table_name: Logical name of the table
            attribute: Attribute metadata definition
            
        Returns:
            Response from API
        """
        url = f"{self.environment_url}/api/data/{self.API_VERSION}/EntityDefinitions(LogicalName='{table_name}')/Attributes"
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    url,
                    headers=self._get_headers(),
                    json=attribute,
                    timeout=30.0
                )
                
                if response.status_code in [200, 201, 204]:
                    logger.info(f"Successfully created field {attribute['SchemaName']} on {table_name}")
                    return {
                        "success": True,
                        "schema_name": attribute["SchemaName"],
                        "message": f"Field {attribute['SchemaName']} created successfully"
                    }
                else:
                    error_detail = response.json() if response.text else {}
                    error_msg = error_detail.get("error", {}).get("message", response.text)
                    logger.error(f"Failed to create field: {error_msg}")
                    return {
                        "success": False,
                        "schema_name": attribute["SchemaName"],
                        "error": error_msg
                    }
                    
        except Exception as e:
            logger.error(f"Error creating attribute: {e}")
            return {
                "success": False,
                "schema_name": attribute.get("SchemaName", "unknown"),
                "error": str(e)
            }
    
    def create_field(
        self,
        table_name: str,
        field_definition: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a field based on field definition from UI
        
        Args:
            table_name: Logical name of the table
            field_definition: Field definition with schemaName, displayName, type, etc.
            
        Returns:
            Result dict with success status and message
        """
        schema_name = field_definition.get("schemaName")
        display_name = field_definition.get("displayName")
        field_type = field_definition.get("type")
        required = field_definition.get("required", False)
        max_length = field_definition.get("maxLength")
        description = field_definition.get("description", "")
        
        # Route to appropriate field creation method
        if field_type in ["Text", "String"]:
            return self.create_string_field(
                table_name,
                schema_name,
                display_name,
                max_length=max_length or 100,
                required=required,
                description=description
            )
        elif field_type in ["Number", "Integer"]:
            return self.create_integer_field(
                table_name,
                schema_name,
                display_name,
                required=required,
                description=description
            )
        elif field_type in ["Boolean", "TwoOptions"]:
            return self.create_boolean_field(
                table_name,
                schema_name,
                display_name,
                required=required,
                description=description
            )
        elif field_type in ["Date", "DateTime"]:
            include_time = field_type == "DateTime"
            return self.create_datetime_field(
                table_name,
                schema_name,
                display_name,
                required=required,
                include_time=include_time,
                description=description
            )
        else:
            return {
                "success": False,
                "schema_name": schema_name,
                "error": f"Unsupported field type: {field_type}"
            }
    
    def get_table_metadata(self, table_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a table
        
        Args:
            table_name: Logical name of the table
            
        Returns:
            Table metadata or None if not found
        """
        url = f"{self.environment_url}/api/data/{self.API_VERSION}/EntityDefinitions(LogicalName='{table_name}')"
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    url,
                    headers=self._get_headers(),
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    return response.json()
                else:
                    logger.warning(f"Table {table_name} not found or error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting table metadata: {e}")
            return None
