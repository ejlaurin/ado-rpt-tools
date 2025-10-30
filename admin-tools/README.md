### ✅ Key Setup Requirements

- **Service Connection**: Replace `<Your-Service-Connection-Name>` with a valid Azure DevOps service connection.
- **OAuth Token Access**: Ensure the pipeline has “Allow scripts to access OAuth token” enabled.
- **Organization URL**: Uses `$(System.CollectionId)` to dynamically resolve the current organization.

### 🧠 Optional Enhancements

- Save results to a file and publish as an artifact.
- Filter by specific domains or roles.
- Export to CSV for audit or compliance workflows.

Would you like help turning this into a reusable template or integrating it with a compliance dashboard?

