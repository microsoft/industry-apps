"""
Dataverse Client for Field Creation, Management, and Record Operations.
Handles authentication and API calls to Dataverse Web API.
"""

import json
import logging
import re
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
        "Date Time": "DateTime",
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
        """
        Create a single-line text field
        
        Args:
            schema_name: PascalCase schema name (e.g., "appbase_PositionNumber")
        """
        # Generate lowercase logical name from schema name
        logical_name = schema_name.lower()
        
        attribute = {
            "@odata.type": "Microsoft.Dynamics.CRM.StringAttributeMetadata",
            "AttributeType": "String",
            "AttributeTypeName": {
                "Value": "StringType"
            },
            "SchemaName": schema_name,
            "LogicalName": logical_name,
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
        # Generate lowercase logical name from schema name
        logical_name = schema_name.lower()
        
        attribute = {
            "@odata.type": "Microsoft.Dynamics.CRM.IntegerAttributeMetadata",
            "AttributeType": "Integer",
            "AttributeTypeName": {
                "Value": "IntegerType"
            },
            "SchemaName": schema_name,
            "LogicalName": logical_name,
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
        # Generate lowercase logical name from schema name
        logical_name = schema_name.lower()
        
        attribute = {
            "@odata.type": "Microsoft.Dynamics.CRM.BooleanAttributeMetadata",
            "AttributeType": "Boolean",
            "AttributeTypeName": {
                "Value": "BooleanType"
            },
            "SchemaName": schema_name,
            "LogicalName": logical_name,
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
    
    def create_picklist_field(
        self,
        table_name: str,
        schema_name: str,
        display_name: str,
        option_set_schema_name: str,
        required: bool = False,
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a choice (picklist) field that references an existing global option set"""
        # Generate lowercase logical name from schema name
        logical_name = schema_name.lower()
        
        # First, get the global option set metadata to obtain its GUID
        optionset_metadata = self.get_global_optionset_metadata(option_set_schema_name)
        if not optionset_metadata:
            return {
                "success": False,
                "schema_name": schema_name,
                "error": f"Global option set '{option_set_schema_name}' not found in Dataverse"
            }
        
        optionset_id = optionset_metadata.get("MetadataId")
        if not optionset_id:
            return {
                "success": False,
                "schema_name": schema_name,
                "error": f"Could not retrieve MetadataId for global option set '{option_set_schema_name}'"
            }
        
        attribute = {
            "@odata.type": "Microsoft.Dynamics.CRM.PicklistAttributeMetadata",
            "AttributeType": "Picklist",
            "AttributeTypeName": {
                "Value": "PicklistType"
            },
            "SchemaName": schema_name,
            "LogicalName": logical_name,
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
            "GlobalOptionSet@odata.bind": f"/GlobalOptionSetDefinitions({optionset_id})"
        }
        
        return self._create_attribute(table_name, attribute)
    
    def create_lookup_relationship(
        self,
        source_table: str,
        field_schema_name: str,
        field_display_name: str,
        target_table_logical_name: str,
        description: str = ""
    ) -> Dict[str, Any]:
        """
        Create a lookup field by establishing a N:1 relationship
        
        Args:
            source_table: Table where the lookup field will be created (referencing entity)
            field_schema_name: Schema name of the lookup field (e.g., appbase_primarycontactid)
            field_display_name: Display name of the lookup field
            target_table_logical_name: Logical name of the target table (referenced entity)
            description: Optional description
            
        Returns:
            Result dict with success status and message
        """
        # Schema name comes from frontend already in PascalCase (e.g., appbase_ContentTemplate)
        # Just use it as-is for schema, create lowercase version for logical name
        parts = field_schema_name.split('_')
        if len(parts) > 1:
            prefix = parts[0]
            field_part = '_'.join(parts[1:])  # Rejoin in case there are multiple underscores
            schema_name_pascal = field_schema_name  # Use as-is (already PascalCase from frontend)
            # Logical name: prefix + lowercase field part (no underscores)
            logical_name = f"{prefix}_{field_part.replace('_', '').lower()}"
        else:
            schema_name_pascal = field_schema_name
            logical_name = field_schema_name.lower()
        
        # Extract publisher prefix
        prefix = parts[0] if len(parts) > 0 else 'new'
        
        # Clean field name for relationship name (remove prefix)
        field_name_cleaned = field_schema_name
        if field_schema_name.startswith(prefix + '_'):
            field_name_cleaned = field_schema_name[len(prefix) + 1:]
        
        # Generate relationship schema name: {sourcetable}_{fieldname}
        # Don't add prefix again since source table already has it
        relationship_name = f"{source_table}_{field_name_cleaned}"
        
        # Detect self-referential relationship
        is_hierarchical = (source_table.lower() == target_table_logical_name.lower())
        
        # Assume primary key follows pattern: {tablename}id
        target_primary_key = f"{target_table_logical_name}id"
        
        # Build relationship metadata
        relationship_metadata = {
            "@odata.type": "Microsoft.Dynamics.CRM.OneToManyRelationshipMetadata",
            "SchemaName": relationship_name,
            "ReferencedEntity": target_table_logical_name,
            "ReferencedAttribute": target_primary_key,
            "ReferencingEntity": source_table,
            "RelationshipBehavior": 1,  # Parental
            "IsHierarchical": is_hierarchical,
            "IsCustomizable": {
                "Value": True
            },
            "CascadeConfiguration": {
                "Assign": "NoCascade",
                "Delete": "RemoveLink",
                "Merge": "NoCascade",
                "Reparent": "NoCascade",
                "Share": "NoCascade",
                "Unshare": "NoCascade"
            },
            "Lookup": {
                "@odata.type": "Microsoft.Dynamics.CRM.LookupAttributeMetadata",
                "SchemaName": schema_name_pascal,
                "LogicalName": logical_name,
                "DisplayName": {
                    "@odata.type": "Microsoft.Dynamics.CRM.Label",
                    "LocalizedLabels": [
                        {
                            "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                            "Label": field_display_name,
                            "LanguageCode": 1033
                        }
                    ]
                },
                "RequiredLevel": {
                    "Value": "None",
                    "CanBeChanged": True
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
                }
            }
        }
        
        url = f"{self.environment_url}/api/data/{self.API_VERSION}/RelationshipDefinitions"
        
        try:
            with httpx.Client() as client:
                response = client.post(
                    url,
                    headers=self._get_headers(),
                    json=relationship_metadata,
                    timeout=120.0  # Increased timeout for lookup relationship creation (can take 30-90 seconds)
                )
                
                if response.status_code in [200, 201, 204]:
                    logger.info(f"Successfully created lookup relationship: {relationship_name}")
                    return {
                        "success": True,
                        "schema_name": schema_name_pascal,
                        "relationship_name": relationship_name,
                        "message": f"Lookup field '{field_display_name}' created successfully"
                    }
                else:
                    error_detail = response.text
                    try:
                        error_json = response.json()
                        error_detail = error_json.get("error", {}).get("message", response.text)
                    except:
                        pass
                    
                    logger.error(f"Failed to create lookup relationship: {response.status_code} - {error_detail}")
                    return {
                        "success": False,
                        "schema_name": schema_name_pascal,
                        "error": f"API error {response.status_code}: {error_detail}"
                    }
                    
        except Exception as e:
            logger.error(f"Error creating lookup relationship: {e}")
            return {
                "success": False,
                "schema_name": field_schema_name,
                "error": str(e)
            }
    
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
        # Generate lowercase logical name from schema name
        logical_name = schema_name.lower()
        
        attribute = {
            "@odata.type": "Microsoft.Dynamics.CRM.DateTimeAttributeMetadata",
            "AttributeType": "DateTime",
            "AttributeTypeName": {
                "Value": "DateTimeType"
            },
            "SchemaName": schema_name,
            "LogicalName": logical_name,
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
    
    def create_memo_field(
        self,
        table_name: str,
        schema_name: str,
        display_name: str,
        max_length: int = 2000,
        required: bool = False,
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a multiline text (memo) field"""
        # Generate lowercase logical name from schema name
        logical_name = schema_name.lower()
        
        attribute = {
            "@odata.type": "Microsoft.Dynamics.CRM.MemoAttributeMetadata",
            "AttributeType": "Memo",
            "AttributeTypeName": {
                "Value": "MemoType"
            },
            "SchemaName": schema_name,
            "LogicalName": logical_name,
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
            "Format": "Text"
        }
        
        return self._create_attribute(table_name, attribute)
    
    def create_richtext_field(
        self,
        table_name: str,
        schema_name: str,
        display_name: str,
        max_length: int = 1048576,
        required: bool = False,
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a multi-line rich text field"""
        # Generate lowercase logical name from schema name
        logical_name = schema_name.lower()
        
        attribute = {
            "@odata.type": "Microsoft.Dynamics.CRM.MemoAttributeMetadata",
            "AttributeType": "Memo",
            "AttributeTypeName": {
                "Value": "MemoType"
            },
            "SchemaName": schema_name,
            "LogicalName": logical_name,
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
            "Format": "RichText"
        }
        
        return self._create_attribute(table_name, attribute)
    
    def create_url_field(
        self,
        table_name: str,
        schema_name: str,
        display_name: str,
        max_length: int = 200,
        required: bool = False,
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a URL formatted text field"""
        
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
                "Value": "Url"
            }
        }
        
        return self._create_attribute(table_name, attribute)
    
    def create_decimal_field(
        self,
        table_name: str,
        schema_name: str,
        display_name: str,
        required: bool = False,
        precision: int = 2,
        min_value: float = -100000000000.0,
        max_value: float = 100000000000.0,
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a decimal (float) field"""
        # Generate lowercase logical name from schema name
        logical_name = schema_name.lower()
        
        attribute = {
            "@odata.type": "Microsoft.Dynamics.CRM.DecimalAttributeMetadata",
            "AttributeType": "Decimal",
            "AttributeTypeName": {
                "Value": "DecimalType"
            },
            "SchemaName": schema_name,
            "LogicalName": logical_name,
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
            "Precision": precision,
            "MinValue": min_value,
            "MaxValue": max_value
        }
        
        return self._create_attribute(table_name, attribute)
    
    def create_currency_field(
        self,
        table_name: str,
        schema_name: str,
        display_name: str,
        required: bool = False,
        precision: int = 2,
        min_value: float = -922337203685477.0,
        max_value: float = 922337203685477.0,
        description: str = ""
    ) -> Dict[str, Any]:
        """Create a currency (money) field"""
        
        attribute = {
            "@odata.type": "Microsoft.Dynamics.CRM.MoneyAttributeMetadata",
            "AttributeType": "Money",
            "AttributeTypeName": {
                "Value": "MoneyType"
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
            "Precision": precision,
            "PrecisionSource": 2,
            "MinValue": min_value,
            "MaxValue": max_value
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
        elif field_type in ["Memo", "MultilineText"]:
            return self.create_memo_field(
                table_name,
                schema_name,
                display_name,
                max_length=max_length or 4000,
                required=required,
                description=description
            )
        elif field_type in ["RichText", "HTML", "Rich"]:
            return self.create_richtext_field(
                table_name,
                schema_name,
                display_name,
                max_length=max_length or 1048576,
                required=required,
                description=description
            )
        elif field_type in ["URL", "Url"]:
            return self.create_url_field(
                table_name,
                schema_name,
                display_name,
                max_length=max_length or 200,
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
        elif field_type in ["Decimal", "Float", "Double"]:
            return self.create_decimal_field(
                table_name,
                schema_name,
                display_name,
                required=required,
                description=description
            )
        elif field_type in ["Currency", "Money"]:
            return self.create_currency_field(
                table_name,
                schema_name,
                display_name,
                required=required,
                description=description
            )
        elif field_type in ["Boolean", "TwoOptions", "YesNo", "Yes / No"]:
            # Map Yes/No fields to the custom appbase_yesno choice field
            return self.create_picklist_field(
                table_name,
                schema_name,
                display_name,
                option_set_schema_name="appbase_yesno",
                required=required,
                description=description
            )
        elif field_type in ["Choice", "Picklist"]:
            option_set_schema_name = field_definition.get("optionSetSchemaName")
            if not option_set_schema_name:
                return {
                    "success": False,
                    "schema_name": schema_name,
                    "error": "Choice fields require optionSetSchemaName"
                }
            return self.create_picklist_field(
                table_name,
                schema_name,
                display_name,
                option_set_schema_name=option_set_schema_name,
                required=required,
                description=description
            )
        elif field_type in ["Date", "DateTime", "Date Time"]:
            include_time = field_type in ["DateTime", "Date Time"]
            return self.create_datetime_field(
                table_name,
                schema_name,
                display_name,
                required=required,
                include_time=include_time,
                description=description
            )
        elif field_type in ["Lookup", "Reference"]:
            target_table = field_definition.get("targetTableLogicalName")
            if not target_table:
                return {
                    "success": False,
                    "schema_name": schema_name,
                    "error": "Lookup fields require targetTableLogicalName"
                }
            return self.create_lookup_relationship(
                source_table=table_name,
                field_schema_name=schema_name,
                field_display_name=display_name,
                target_table_logical_name=target_table,
                description=description
            )
        else:
            return {
                "success": False,
                "schema_name": schema_name,
                "error": f"Unsupported field type: {field_type}"
            }
    
    def create_global_optionset(
        self,
        schema_name: str,
        display_name: str,
        description: str,
        options: List[Dict[str, Any]],
        solution_unique_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a global option set
        
        Args:
            schema_name: Schema name for the option set (e.g., "appbase_priority")
            display_name: Display name (e.g., "Priority")
            description: Description of the option set
            options: List of options with 'value' and 'label' keys
            solution_unique_name: Optional unique name of solution to add to
            
        Returns:
            Dictionary with success status and details
        """
        url = f"{self.environment_url}/api/data/{self.API_VERSION}/GlobalOptionSetDefinitions"
        
        # Build options array
        option_metadata = []
        for opt in options:
            option_metadata.append({
                "Value": opt["value"],
                "Label": {
                    "@odata.type": "Microsoft.Dynamics.CRM.Label",
                    "LocalizedLabels": [
                        {
                            "@odata.type": "Microsoft.Dynamics.CRM.LocalizedLabel",
                            "Label": opt["label"],
                            "LanguageCode": 1033  # English
                        }
                    ]
                }
            })
        
        # Build request body
        optionset_metadata = {
            "@odata.type": "Microsoft.Dynamics.CRM.OptionSetMetadata",
            "Name": schema_name,
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
                        "Label": description or "",
                        "LanguageCode": 1033
                    }
                ]
            },
            "OptionSetType": "Picklist",
            "IsGlobal": True,
            "Options": option_metadata
        }
        
        try:
            # Get base headers
            headers = self._get_headers()
            
            # Add solution context header if specified
            if solution_unique_name:
                headers["MSCRM.SolutionUniqueName"] = solution_unique_name
                logger.info(f"Creating global option set in solution: {solution_unique_name}")
            
            with httpx.Client() as client:
                response = client.post(
                    url,
                    headers=headers,
                    json=optionset_metadata,
                    timeout=120.0  # Increased timeout for option set creation (can take time when adding to solution)
                )
                
                if response.status_code in [200, 201, 204]:
                    logger.info(f"Successfully created global option set: {schema_name}")
                    return {
                        "success": True,
                        "schema_name": schema_name,
                        "display_name": display_name,
                        "message": f"Global option set '{display_name}' created successfully"
                    }
                else:
                    error_detail = response.text
                    try:
                        error_json = response.json()
                        error_detail = error_json.get("error", {}).get("message", response.text)
                    except:
                        pass
                    
                    logger.error(f"Failed to create global option set: {response.status_code} - {error_detail}")
                    return {
                        "success": False,
                        "schema_name": schema_name,
                        "error": f"API error {response.status_code}: {error_detail}"
                    }
                    
        except Exception as e:
            logger.error(f"Error creating global option set: {e}")
            return {
                "success": False,
                "schema_name": schema_name,
                "error": str(e)
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
    
    def get_global_optionset_metadata(self, option_set_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a global option set by name
        
        Args:
            option_set_name: Name (schema name) of the global option set
            
        Returns:
            Option set metadata or None if not found
        """
        url = f"{self.environment_url}/api/data/{self.API_VERSION}/GlobalOptionSetDefinitions(Name='{option_set_name}')"
        
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
                    logger.warning(f"Global option set {option_set_name} not found or error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error getting global option set metadata: {e}")
            return None
    
    def get_entity_definitions(self) -> List[Dict[str, Any]]:
        """
        Get all entity (table) definitions from Dataverse
        
        Returns:
            List of tables with logical name, display name, and primary key attribute
        """
        url = f"{self.environment_url}/api/data/{self.API_VERSION}/EntityDefinitions"
        params = {
            "$select": "LogicalName,DisplayName,PrimaryIdAttribute,IsCustomEntity"
        }
        
        try:
            logger.info(f"Querying entity definitions from {url}")
            with httpx.Client() as client:
                response = client.get(
                    url,
                    headers=self._get_headers(),
                    params=params,
                    timeout=30.0
                )
                
                logger.info(f"Entity definitions response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    entities = []
                    
                    for entity in data.get("value", []):
                        logical_name = entity.get("LogicalName", "")
                        display_name_obj = entity.get("DisplayName", {})
                        
                        # Filter to custom entities and common system tables
                        is_custom = entity.get("IsCustomEntity", False)
                        is_common_system = logical_name in ['account', 'contact', 'systemuser', 'team']
                        
                        if not (is_custom or is_common_system):
                            continue
                        
                        # Extract display name from LocalizedLabels
                        display_name = logical_name  # fallback
                        if display_name_obj and "LocalizedLabels" in display_name_obj:
                            labels = display_name_obj.get("LocalizedLabels", [])
                            if labels and len(labels) > 0:
                                display_name = labels[0].get("Label", logical_name)
                        
                        entities.append({
                            "logicalName": logical_name,
                            "displayName": display_name,
                            "primaryIdAttribute": entity.get("PrimaryIdAttribute", f"{logical_name}id")
                        })
                    
                    # Sort by display name since $orderby not supported on EntityDefinitions
                    entities.sort(key=lambda e: e["displayName"].lower())
                    
                    logger.info(f"Retrieved {len(entities)} entity definitions")
                    return entities
                else:
                    error_detail = response.text
                    try:
                        error_json = response.json()
                        error_detail = error_json.get("error", {}).get("message", response.text)
                    except:
                        pass
                    logger.error(f"Failed to get entity definitions: {response.status_code} - {error_detail}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting entity definitions: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_global_optionset_definitions(self) -> List[Dict[str, Any]]:
        """
        Get all global option set definitions from Dataverse
        
        Returns:
            List of global option sets with schema name, display name, and options
        """
        url = f"{self.environment_url}/api/data/{self.API_VERSION}/GlobalOptionSetDefinitions"
        params = {
            "$select": "Name,DisplayName,IsCustomOptionSet"
        }
        
        try:
            logger.info(f"Querying global option set definitions from {url}")
            with httpx.Client() as client:
                response = client.get(
                    url,
                    headers=self._get_headers(),
                    params=params,
                    timeout=30.0
                )
                
                logger.info(f"Global option set definitions response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    option_sets = []
                    
                    for optionset in data.get("value", []):
                        schema_name = optionset.get("Name", "")
                        display_name_obj = optionset.get("DisplayName", {})
                        
                        # Filter to custom option sets (exclude system option sets by default)
                        is_custom = optionset.get("IsCustomOptionSet", False)
                        
                        if not is_custom:
                            continue
                        
                        # Extract display name from LocalizedLabels
                        display_name = schema_name  # fallback
                        if display_name_obj and "LocalizedLabels" in display_name_obj:
                            labels = display_name_obj.get("LocalizedLabels", [])
                            if labels and len(labels) > 0:
                                display_name = labels[0].get("Label", schema_name)
                        
                        option_sets.append({
                            "schemaName": schema_name,
                            "displayName": display_name
                        })
                    
                    # Sort by display name
                    option_sets.sort(key=lambda o: o["displayName"].lower())
                    
                    logger.info(f"Retrieved {len(option_sets)} global option set definitions")
                    return option_sets
                else:
                    error_detail = response.text
                    try:
                        error_json = response.json()
                        error_detail = error_json.get("error", {}).get("message", response.text)
                    except:
                        pass
                    logger.error(f"Failed to get global option set definitions: {response.status_code} - {error_detail}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error getting global option set definitions: {e}")
            import traceback
            traceback.print_exc()
            return []

    # -------------------------------------------------------------------------
    # Record operations
    # -------------------------------------------------------------------------

    def get_entity_set_name(self, logical_name: str) -> Optional[str]:
        """
        Return the OData entity set name (collection name) for a logical entity name.

        Args:
            logical_name: Logical name of the table (e.g., "appbase_assetcategory")

        Returns:
            Entity set name (e.g., "appbase_assetcategories") or None if not found
        """
        meta = self.get_table_metadata(logical_name)
        if meta:
            return meta.get("EntitySetName")
        return None

    def create_record(self, entity_set_name: str, fields: Dict[str, Any]) -> Optional[str]:
        """
        Create a record in a Dataverse table.

        Args:
            entity_set_name: OData collection name (e.g., "appbase_assetcategories")
            fields: Dictionary of field logical names to values. Use ``@odata.bind``
                    syntax for lookups, e.g.::

                        {"appbase_assetcategory@odata.bind": "/appbase_assetcategories(guid)"}

        Returns:
            GUID of the created record, or None on failure
        """
        url = f"{self.environment_url}/api/data/{self.API_VERSION}/{entity_set_name}"

        try:
            with httpx.Client() as client:
                response = client.post(
                    url,
                    headers=self._get_headers(),
                    json=fields,
                    timeout=30.0,
                )

                if response.status_code in [200, 201, 204]:
                    # Extract GUID from OData-EntityId header
                    entity_id_header = response.headers.get("OData-EntityId", "")
                    match = re.search(r"\(([0-9a-fA-F-]{36})\)", entity_id_header)
                    if match:
                        guid = match.group(1)
                    else:
                        # 201 responses may include the record in the body
                        try:
                            body = response.json()
                            # Primary key is typically the first key ending in "id"
                            guid = next(
                                (v for k, v in body.items() if k.endswith("id") and isinstance(v, str) and len(v) == 36),
                                None,
                            )
                        except Exception:
                            guid = None

                    logger.info(f"Created record in {entity_set_name}: {guid}")
                    return guid
                else:
                    error_detail = {}
                    try:
                        error_detail = response.json()
                    except Exception:
                        pass
                    error_msg = error_detail.get("error", {}).get("message", response.text)
                    logger.error(f"Failed to create record in {entity_set_name}: {error_msg}")
                    return None

        except Exception as e:
            logger.error(f"Error creating record in {entity_set_name}: {e}")
            return None

    def upsert_record(
        self,
        entity_set_name: str,
        record_id: str,
        fields: Dict[str, Any],
    ) -> bool:
        """
        Upsert a record by GUID (PATCH with If-Match: * suppressed, i.e., unconditional upsert).

        Args:
            entity_set_name: OData collection name
            record_id: GUID of the record to upsert
            fields: Field values to set

        Returns:
            True on success, False on failure
        """
        url = f"{self.environment_url}/api/data/{self.API_VERSION}/{entity_set_name}({record_id})"
        headers = {**self._get_headers(), "If-None-Match": "null"}

        try:
            with httpx.Client() as client:
                response = client.patch(url, headers=headers, json=fields, timeout=30.0)
                if response.status_code in [200, 201, 204]:
                    logger.info(f"Upserted record {record_id} in {entity_set_name}")
                    return True
                else:
                    error_detail = {}
                    try:
                        error_detail = response.json()
                    except Exception:
                        pass
                    error_msg = error_detail.get("error", {}).get("message", response.text)
                    logger.error(f"Failed to upsert record {record_id} in {entity_set_name}: {error_msg}")
                    return False

        except Exception as e:
            logger.error(f"Error upserting record: {e}")
            return False

    def query_records(
        self,
        entity_set_name: str,
        select: Optional[str] = None,
        filter_query: Optional[str] = None,
        top: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Query records from a Dataverse table.

        Args:
            entity_set_name: OData collection name (e.g., "contacts")
            select: Comma-separated field names for $select
            filter_query: OData $filter expression
            top: Maximum number of records to return

        Returns:
            List of record dictionaries
        """
        url = f"{self.environment_url}/api/data/{self.API_VERSION}/{entity_set_name}"
        params: Dict[str, Any] = {"$top": top}
        if select:
            params["$select"] = select
        if filter_query:
            params["$filter"] = filter_query

        try:
            with httpx.Client() as client:
                response = client.get(
                    url,
                    headers=self._get_headers(),
                    params=params,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    records = data.get("value", [])
                    logger.info(f"Queried {len(records)} records from {entity_set_name}")
                    return records
                else:
                    error_detail = {}
                    try:
                        error_detail = response.json()
                    except Exception:
                        pass
                    error_msg = error_detail.get("error", {}).get("message", response.text)
                    logger.error(f"Failed to query {entity_set_name}: {error_msg}")
                    return []

        except Exception as e:
            logger.error(f"Error querying {entity_set_name}: {e}")
            return []
