# Deployment Configuration Update

## Overview
Updated the deployment scripts to use the new `deployments.json` file for tenant and environment selection instead of the previous manual selection methods.

## Changes Made

### 1. Added New Functions to Util.ps1
- **`Get-DeploymentConfig`**: Reads and parses the deployments.json file
- **`Select-Deployment`**: Presents user with deployment options from deployments.json and returns selected deployment configuration

### 2. Updated Scripts

#### Sync-Module.ps1
- Replaced manual tenant/environment selection with config-based selection
- User now selects a deployment (Main/Development) and the script automatically uses the corresponding tenant and environment based on the module type

#### Push-Module.ps1
- Updated to use deployment configuration
- Simplified user experience - just select deployment and module

#### Ship-Module.ps1
- Updated to use deployment configuration
- User selects deployment first, then can choose from available environments within that deployment

#### Deploy-AllModules.ps1
- Updated to use deployment configuration
- User selects deployment and target environment from the config

#### Deploy-Module.ps1
- Updated to use deployment configuration for tenant selection
- Uses config for the three CAST environments (CAST BASE, CAST UTILITY, CAST APPS)

## Configuration Structure
The `deployments.json` file contains:
```json
{
    "Deployments": {
        "Development": {
            "Tenant": "DEV",
            "Environments": {
                "INDUSTRY APPS CORE": "INDUSTRY APPS CORE",
                "INDUSTRY APPS SHARED": "INDUSTRY APPS SHARED",
                "INDUSTRY APPS": "INDUSTRY APPS MODULES"
            }
        },
        "Test": {
            "Tenant": "TEST",
            "Environments": {
                "INDUSTRY APPS CORE": "INDUSTRY APPS CORE",
                "INDUSTRY APPS SHARED": "INDUSTRY APPS SHARED",
                "INDUSTRY APPS": "INDUSTRY APPS MODULES"
            }
        }
    },
    "Modules": {
        "core": {
            "Tenant": "DEV",
            "Environment": "INDUSTRY APPS CORE",
            "DeploymentTargets": ["INDUSTRY APPS SHARED", "INDUSTRY APPS MODULES"]
        },
        "process-automation": {
            "Tenant": "DEV",
            "Environment": "INDUSTRY APPS SHARED",
            "DeploymentTargets": ["INDUSTRY APPS MODULES"]
        }
    },
    "DefaultModule": {
        "Tenant": "DEV",
        "Environment": "INDUSTRY APPS MODULES",
        "DeploymentTargets": ["INDUSTRY APPS MODULES"]
    }
}
```

## Module-to-Environment Mapping
The scripts automatically determine the target environment based on the module:


## Usage
1. Run any deployment script (e.g., `.\scripts\Sync-Module.ps1`)
2. Select the module you want to work with
3. Select the deployment configuration (Development or Test)
4. The script will automatically connect to the appropriate tenant and environment

## Benefits
- Consistent deployment targeting across all scripts
- Easy switching between different deployment environments
- Centralized configuration management
- Reduced user input requirements
- Less chance for manual errors in tenant/environment selection

## Future Enhancements
To add new deployment targets:
1. Add new deployment entry to deployments.json
2. Include tenant and environment mappings
3. All scripts will automatically support the new deployment option