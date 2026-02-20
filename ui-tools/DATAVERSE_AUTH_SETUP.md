# Dataverse Authentication Setup

This guide explains how to set up authentication for Dataverse Web API access in UI Tools.

## Prerequisites

- Azure AD access with ability to register applications
- Dataverse environment access
- System Administrator or System Customizer role in Dataverse

## Step 1: Register Application in Azure AD

1. **Navigate to Azure Portal**
   - Go to https://portal.azure.com
   - Navigate to **Azure Active Directory** → **App registrations**

2. **Create New Registration**
   - Click **"New registration"**
   - **Name**: `Dataverse UI Tools` (or your preferred name)
   - **Supported account types**: Select appropriate option (usually "Accounts in this organizational directory only")
   - **Redirect URI**: Leave blank for service-to-service auth
   - Click **Register**

3. **Note the Application Details**
   - Copy the **Application (client) ID**
   - Copy the **Directory (tenant) ID**
   - You'll need these for configuration

## Step 2: Create Client Secret

1. In your app registration, navigate to **Certificates & secrets**
2. Click **"New client secret"**
3. **Description**: `UI Tools Secret`
4. **Expires**: Choose appropriate expiration (recommend 24 months)
5. Click **Add**
6. **Important**: Copy the secret **Value** immediately (you won't be able to see it again!)

## Step 3: Grant API Permissions

1. Navigate to **API permissions** in your app registration
2. Click **"Add a permission"**
3. Select **Dynamics CRM** (or **Common Data Service** if that's the name)
4. Select **Delegated permissions**
5. Check **user_impersonation**
6. Click **Add permissions**
7. Click **"Grant admin consent for [Your Organization]"** (requires admin privileges)
8. Confirm the consent

## Step 4: Create Application User in Dataverse

1. **Navigate to Power Platform Admin Center**
   - Go to https://admin.powerplatform.microsoft.com
   - Select your environment

2. **Create Application User**
   - Go to **Settings** → **Users + permissions** → **Application users**
   - Click **"+ New app user"**
   - Click **"+ Add an app"**
   - Search for and select your registered app (by client ID or name)
   - **Business unit**: Select appropriate business unit
   - **Security roles**: Assign **System Administrator** or **System Customizer**
   - Click **Create**

## Step 5: Configure UI Tools

1. **Locate Configuration File**
   - Navigate to `.config/deployments.json` in your repository
   - This file contains deployment configurations with embedded authentication settings

2. **Add or Update Deployment Configuration**
   
   Each deployment in `deployments.json` contains its own authentication configuration under the `Auth` key:
   
   ```json
   {
     "Deployments": {
       "Development": {
         "Auth": {
           "TenantId": "your-tenant-id-from-step1",
           "ClientId": "your-client-id-from-step1",
           "ClientSecret": "your-client-secret-from-step2",
           "EnvironmentUrls": {
             "INDUSTRY APPS CORE": "https://orgxxx.crm.dynamics.com",
             "INDUSTRY APPS SHARED": "https://orgyyy.crm.dynamics.com",
             "INDUSTRY APPS": "https://orgzzz.crm.dynamics.com"
           }
         },
         "Environments": {
           "INDUSTRY APPS CORE": "INDUSTRY APPS CORE",
           "INDUSTRY APPS SHARED": "INDUSTRY APPS SHARED",
           "INDUSTRY APPS": "c2fa2ce8-81d7-e002-a65e-8f7800f6bd11"
         }
       },
       "Production": {
         "Auth": {
           "TenantId": "prod-tenant-id",
           "ClientId": "prod-client-id",
           "ClientSecret": "prod-client-secret",
           "EnvironmentUrls": {
             "PROD ENV": "https://prodorg.crm.dynamics.com"
           }
         },
         "Environments": {
           "PROD ENV": "PROD ENV"
         }
       }
     }
   }
   ```

3. **Configuration Steps**
   - Choose a friendly name for your deployment (e.g., "Development", "Production", "Kinetic")
   - Add the deployment to the `Deployments` section
   - Set `Auth.TenantId` to your Azure AD tenant ID from Step 1
   - Set `Auth.ClientId` to your application client ID from Step 1
   - Set `Auth.ClientSecret` to your client secret value from Step 2
   - Add environment URLs to the `Auth.EnvironmentUrls` object

4. **Get Environment URLs**
   - In Power Platform Admin Center, select each environment
   - Copy the **Environment URL** (e.g., `https://org12345.crm.dynamics.com`)
   - Remove any trailing slashes
   - Add to the `EnvironmentUrls` section with the environment name as the key

## Multi-Tenant Support

If you work across multiple Azure AD tenants, each deployment can have different credentials:

- Each deployment has its own app registration via the `Auth` section
- Different deployments can use the same or different Azure AD tenants
- Authentication credentials are embedded directly in each deployment for simplicity
- UI Tools automatically uses the correct credentials based on the selected deployment

## Step 6: Install Python Dependencies

```bash
cd ui-tools/backend
pip install -r requirements.txt
```

This installs:
- `msal` - Microsoft Authentication Library
- `httpx` - HTTP client for API calls

## Step 7: Test the Integration

1. **Start the UI Tools backend**
   ```bash
   cd ui-tools/backend
   python main.py
   ```

2. **Start the frontend** (in another terminal)
   ```bash
   cd ui-tools/frontend
   npm run dev
   ```

3. **Test Field Creation**
   - Navigate to http://localhost:5173
   - Click **"Field Creator"** in the sidebar
   - Select a deployment and environment
   - Enter a test table name (e.g., `account`)
   - Add a test field:
     ```
     cr09x_testfield|Test Field|Text|false|100
     ```
   - Click **"Create Fields"**
   - Watch the streaming output for success/errors

## Security Best Practices

### Production Deployment

For production, consider these security improvements:

1. **Use Azure Key Vault**
   - Store client secret in Azure Key Vault
   - Use Managed Identity for access
   - Update `dataverse_client.py` to retrieve from Key Vault

2. **Use Managed Identity** (if hosted in Azure)
   - Assign Managed Identity to your hosting resource
   - Grant Key Vault access to Managed Identity
   - No client secrets needed!

3. **Rotate Secrets Regularly**
   - Set client secret expiration to 12-24 months
   - Create rotation procedure
   - Monitor expiration dates

4. **Least Privilege**
   - Only grant required security roles to application user
   - Consider custom security role with only field creation permissions
   - Review and audit permissions regularly

### Environment Variables (Alternative)

Instead of JSON file, you can use environment variables:

```bash
# Windows
$env:DATAVERSE_TENANT_ID = "your-tenant-id"
$env:DATAVERSE_CLIENT_ID = "your-client-id"
$env:DATAVERSE_CLIENT_SECRET = "your-client-secret"

# Linux/Mac
export DATAVERSE_TENANT_ID="your-tenant-id"
export DATAVERSE_CLIENT_ID="your-client-id"
export DATAVERSE_CLIENT_SECRET="your-client-secret"
```

Update `main.py` to read from environment variables if preferred.

## Troubleshooting

### Authentication Errors

**Error**: `AADSTS700016: Application not found`
- **Cause**: Client ID is incorrect or app not registered
- **Solution**: Verify client ID matches app registration

**Error**: `AADSTS7000215: Invalid client secret`
- **Cause**: Client secret is incorrect or expired
- **Solution**: Generate new client secret and update config

**Error**: `Insufficient privileges`
- **Cause**: Application user doesn't have required permissions
- **Solution**: Grant System Customizer or System Administrator role to application user

### API Errors

**Error**: `401 Unauthorized`
- **Cause**: Token expired or invalid
- **Solution**: Client will automatically retrieve new token

**Error**: `Principal user is missing prvCreateAttribute privilege`
- **Cause**: Application user missing field creation permissions
- **Solution**: Ensure application user has System Customizer or higher role

**Error**: `Table [name] not found`
- **Cause**: Table doesn't exist or incorrect logical name
- **Solution**: Verify table name is correct logical name (not display name)

**Error**: `Field [name] already exists`
- **Cause**: Field with that schema name already exists
- **Solution**: Use different schema name or delete existing field first

### Connection Issues

**Error**: `Environment URL not configured`
- **Cause**: Environment URL missing from deployment Auth.EnvironmentUrls configuration
- **Solution**: Add environment URL to the `Auth.EnvironmentUrls` section in your deployment

**Error**: `Connection timeout`
- **Cause**: Network issues or incorrect environment URL
- **Solution**: Verify environment URL is accessible and correct

## Support

For issues or questions:
1. Check console/terminal output for detailed error messages
2. Verify all configuration steps completed
3. Test authentication separately using Power Platform CLI
4. Review Azure AD audit logs for authentication failures

## Additional Resources

- [Microsoft Dataverse Web API Reference](https://docs.microsoft.com/power-apps/developer/data-platform/webapi/overview)
- [Azure AD App Registration](https://docs.microsoft.com/azure/active-directory/develop/quickstart-register-app)
- [Dataverse Application Users](https://docs.microsoft.com/power-platform/admin/manage-application-users)
- [MSAL Python Documentation](https://msal-python.readthedocs.io/)
