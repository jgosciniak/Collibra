# Configuring Single Sign-On (SSO) for Collibra Data Quality using Azure AD

## Overview

This document provides a step-by-step guide for configuring Single Sign-On (SSO) integration between Collibra Data Quality (DQ) and Microsoft Azure Active Directory (Azure AD). By implementing SSO, you can:

- Centrally control who has access to Collibra DQ through Azure AD
- Enable automatic sign-in to Collibra DQ using Azure AD credentials
- Manage user accounts and access permissions from a single location
- Enforce security policies consistently across applications

## Prerequisites

Before you begin the configuration, ensure you have:

- A Microsoft Azure subscription with administrative access
- An Azure AD tenant with sufficient permissions (Application Administrator, Cloud Application Administrator, or Application Owner role)
- A Collibra DQ instance with administrative access
- Basic understanding of SAML authentication concepts

## Configuration Steps

The configuration process includes steps on both the Azure AD side and the Collibra DQ side.

### Part 1: Configure Azure AD

1. **Add Collibra from the Azure AD Gallery**
   
   a. Sign in to the [Microsoft Entra admin center](https://entra.microsoft.com)
   
   b. Navigate to **Entra ID** > **Enterprise applications** > **New application**
   
   c. Search for "Collibra" in the gallery
   
   d. Select **Collibra** from the results and click **Add**

2. **Configure SAML Settings in Azure AD**
   
   a. Navigate to **Entra ID** > **Enterprise apps** > **Collibra** > **Single sign-on**
   
   b. Select **SAML** as the single sign-on method
   
   c. Configure the Basic SAML settings:
      - **Identifier (Entity ID)**: `https://<INSTANCE_NAME>.collibra.com/`
      - **Reply URL**: `https://<INSTANCE_NAME>.collibra.com/`
      - **Sign on URL**: `https://<INSTANCE_NAME>.collibra.com/` (for SP-initiated mode)
   
   d. Configure User Attributes & Claims exactly as follows:

      **Required claim:**
      - **Unique User Identifier (Name ID)**: user.userprincipalname

      **Additional claims:**
      - **http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress**: user.mail
      - **http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname**: user.givenname
      - **http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name**: user.userprincipalname
      - **http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname**: user.surname
      - **memberOf**: user.groups
   
   e. In the **SAML Signing Certificate** section, copy the **App Federation Metadata Url** for later use in Collibra DQ configuration

3. **Assign Users and Groups to the Application**
   
   a. Navigate to **Entra ID** > **Enterprise apps** > **Collibra** > **Users and groups**
   
   b. Click **Add user/group**
   
   c. Select the users or groups who should have access to Collibra DQ
   
   d. Click **Assign**

4. **Configure Group Claims (if using group-based access control)**
   
   a. If you're using Azure AD groups for access control in Collibra DQ, ensure the groups claim is properly configured
   
   b. For Azure AD environments with many groups, you'll need to handle the groups.link claim (see the Advanced Configuration section below)
   
   c. Note that Azure AD will send group GUIDs in the SAML response, which will need to be mapped to roles in Collibra DQ

### Part 2: Configure Collibra DQ

1. **Set Required Environment Variables**
   
   **For standalone installation:**
   
   a. Edit the `owl-env.sh` file located in `<installation_directory>/owl/config/`
   
   b. Add or modify the following required properties:
   
   ```bash
   # Required SAML Properties
   export SAML_ENABLED=true
   export SAML_ENTITY_ID=Collibra_DQ
   
   # CORS Configuration (Required for SAML)
   export CORS_ALLOWED_ORIGINS=https://login.microsoftonline.com,https://<your-dq-instance-url>
   
   # Azure AD Specific Configuration
   export SAML_USER_NAME_PROP="http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name"
   export SAML_ROLES_PROP_NAME="memberOf"
   
   # Optional but Recommended Settings
   export SAML_METADATA_USE_URL=true
   export SAML_GRANT_ALL_PUBLIC=true
   ```
   
   **For cloud-native installation:**
   
   a. Add these properties to your DQ-web ConfigMap
   
   b. Recycle the pod after making changes

2. **Configure SAML in the Collibra DQ Admin Console**
   
   a. Sign in to Collibra DQ as an administrator and select the tenant you want to configure
   
   b. Navigate to **Admin Console** > **User Management** > **SAML Security**
   
   c. From the **SAML Enabled** dropdown menu, select **Enabled**
   
   d. Click the + button to add a new metadata configuration
   
   e. In the **Add Meta Data Configuration** dialog, enter:
      - **Meta-Data URL**: Paste the App Federation Metadata Url copied from Azure AD
      - **Meta-Data Label**: A descriptive name (e.g., "Azure AD SSO")
      - **IDP_URL**: The Azure AD login URL (typically `https://login.microsoftonline.com/<tenant-id>/saml2`)
   
   f. Click **Add**
   
   g. Restart Collibra DQ to apply the changes

3. **Map Azure AD Groups to Collibra DQ Roles** (if using group-based access control)
   
   a. In Collibra DQ, navigate to **Admin Console** > **User Management** > **AD Group to Role Mapping**
   
   b. Add mappings between Azure AD group IDs and Collibra DQ roles
   
   c. Note that Azure AD sends GUIDs for groups, so you'll need to identify the correct group IDs from Azure AD

4. **Download Service Provider Metadata for Reference**
   
   a. You can download the Collibra DQ service provider metadata from:
      ```
      https://<your_dq_environment_url>/saml/metadata
      ```
   
   b. This metadata may be needed if you encounter issues with the configuration

## Advanced Configuration

### Handling Azure AD Group Links

When Azure AD SSO sends more than five groups for a user, it sends a groups.link assertion instead of the actual groups. To handle this:

1. Add the following properties to your `owl-env.sh` file:
   
   ```bash
   # Azure AD Group Link Configuration
   export SAML_GROUPS_LINK_PROP="http://schemas.microsoft.com/claims/groups.link"
   export AZURE_CLIENT_ID="<your-azure-client-id>"
   export AZURE_CLIENT_SECRET="<your-azure-client-secret>"
   ```

2. Obtain a client key from Azure by following [Microsoft's documentation on creating an application secret](https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-create-service-principal-portal#option-2-create-a-new-application-secret)

3. Ensure the application has the MS Graph API application permission `directory.read.all`

4. Verify that the Sign-on URL is not populated in the IdP setup in Azure

### Load Balancer Configuration

If Collibra DQ is behind a load balancer, add these additional properties:

```bash
export SAML_LB_EXISTS=true
export SAML_LB_SCHEME=https
export SAML_LB_PORT=443
export SAML_LB_SERVER_NAME=<your-load-balancer-hostname>
export SAML_LB_INCLUDE_PORT_IN_REQUEST=false
```

## Testing the Configuration

1. **Test SP-initiated SSO:**
   - Access your Collibra DQ login page directly
   - Click on the "Sign in with SSO" option
   - You should be redirected to Azure AD for authentication
   - After successful authentication, you should be redirected back to Collibra DQ

2. **Test IDP-initiated SSO:**
   - Sign in to the Azure portal
   - Navigate to **Entra ID** > **Enterprise applications** > **All applications**
   - Find and click on the Collibra application
   - Click on **Test this application**
   - You should be automatically signed in to Collibra DQ

## Exact Azure AD Claims Configuration

The screenshot below shows exactly how the Attributes & Claims section should be configured in Azure AD:

```
Attributes & Claims

Required claim
Claim name                          Type    Value
Unique User Identifier (Name ID)    SAML    user.userprincipalname

Additional claims
Claim name                                                   Type    Value
http://schemas.xmlsoap.org/ws/2005/05/identity/claims/emailaddress    SAML    user.mail
http://schemas.xmlsoap.org/ws/2005/05/identity/claims/givenname       SAML    user.givenname
http://schemas.xmlsoap.org/ws/2005/05/identity/claims/name            SAML    user.userprincipalname
http://schemas.xmlsoap.org/ws/2005/05/identity/claims/surname         SAML    user.surname
memberOf                                                               SAML    user.groups
```

## Troubleshooting

### Common Issues

1. **SAML Response Validation Errors**
   - Verify that the Entity ID and Reply URL in Azure AD match what's expected by Collibra DQ
   - Check the SAML response using browser developer tools to identify specific errors

2. **User Not Authorized Error**
   - Ensure the user is assigned to the Collibra application in Azure AD
   - Check that group mappings are correctly configured in Collibra DQ
   - Verify that SAML_GRANT_ALL_PUBLIC is set to true if you want to allow all authenticated users

3. **CORS Issues**
   - Ensure CORS_ALLOWED_ORIGINS includes both your IDP URL and DQ URL
   - Check browser console for CORS-related errors

4. **Group Membership Not Working**
   - For more than 5 groups, ensure you've configured the groups.link handling
   - Verify Azure application permissions include directory.read.all
   - Confirm group-to-role mappings use the correct Azure AD group IDs (GUIDs)

### Viewing SAML Responses

To debug SAML issues, you can view the SAML response:

1. Install a SAML tracer extension in your browser
2. Attempt the SSO login
3. Check the SAML tracer output to see the SAML request and response
4. Verify the attributes sent by Azure AD match those expected by Collibra DQ

## Security Considerations

1. Always transmit SAML assertions over HTTPS
2. Rotate Azure client secrets periodically
3. Use the most restrictive permissions necessary for the Azure AD application
4. Implement conditional access policies in Azure AD for additional security
5. Regularly audit user access and group assignments

## References

- [Collibra DQ SAML Authentication Documentation](https://productresources.collibra.com/docs/collibra/latest/Content/DataQuality/SAML%20Authentication.htm)
- [Configuring SAML SSO for Azure with Collibra DQ](https://productresources.collibra.com/docs/collibra/latest/Content/DataQuality/DQSecurity/ta_saml-sso-azure-config.htm)
- [Microsoft Entra SSO Integration with Collibra](https://learn.microsoft.com/en-us/entra/identity/saas-apps/collibra-tutorial)
- [Azure AD SAML Token Reference](https://learn.microsoft.com/en-us/azure/active-directory/develop/reference-saml-tokens)
