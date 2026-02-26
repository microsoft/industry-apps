# FAST - Frontier App & AI Starter Templates

Welcome to FAST (Frontier App & AI Starter Templates), a collection of standardized, reusable starter app templates for Microsoft Dataverse, purpose-built for common business processes across industries. Each module defines entities, relationships, and field specifications that align with real-world operational needs. By adopting these apps, organizations and solution builders can accelerate Power Platform and Dynamics 365 deployments, ensure data consistency across programs, and reduce the cost of custom development. Whether you are building case management, process tracking, asset management, or other business solutions, these modules provide a ready-to-use foundation that is extensible, interoperable, and maintained under an open MIT license.

## 📁 Repository Structure

Solutions are organized into domain-based categories:

### Solution Categories

- **administrative/** - Executive coordination, member organizations
- **compliance-security/** - Investigations, personnel security
- **external-engagement/** - Event management, external interactions, programs and services
- **financial/** - Financial management and accounting
- **government/** - Civic engagement, court case management, legislative operations, gov-core
- **operations/** - Asset management, facilities, IT service management, operational excellence, project tracking, request tracker
- **shared/** - Core shared components, data integration, process automation
- **workforce/** - HR administration, benefits, recruiting, training, knowledge management, time tracking, gamification

### Supporting Tools

- **ui-tools/** - Web-based management interface for Dataverse operations (FastAPI backend, Vite frontend, Dataverse client library)
- **data-generator/** - Utilities for generating and validating test data

Each solution module typically contains:

- Dataverse solution files (.cdsproj)
- Entity definitions and relationships
- BUILD.md documentation
- PowerShell deployment scripts

## 🛠️ Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit [Contributor License Agreements](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

We are working on integrating the full unpacked solution files for a more direct contribution experience. Check back for updates for availability.

## ™️ Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.

## 📌 Intended Use

The modules in this repository are provided as **reference implementations** for learning, experimentation, and as a starting point for building production-ready applications.

They are **not** designed to be deployed directly to a production environment without additional development, testing, and validation. Any organization planning to use these modules in production should:

* Adapt and extend the solutions to meet specific business and technical requirements
* Integrate them into the organization’s **Application Lifecycle Management (ALM)** processes
* Perform full **security, compliance, and performance reviews**
* Apply updates, fixes, and enhancements as needed

These modules are meant to accelerate solution design and reduce initial build time, but the responsibility for ensuring readiness, compliance, and ongoing maintenance lies with the implementing organization.

## ⚖️ Support 

The modules in this repository are provided **“as is”** without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement.

As open source, these solutions are **not** official Microsoft products and are **not** covered by any Microsoft support agreement or service-level commitment. No guarantee is made regarding the accuracy, completeness, performance, or continued availability of these modules.

Use of these modules is at your own risk. You are responsible for evaluating their suitability for your environment, performing necessary security reviews, and ensuring compliance with applicable laws, regulations, and policies.

By installing or using these modules, you acknowledge that no obligation exists for Microsoft or the repository maintainers to provide support, updates, or maintenance, and that any assistance provided is voluntary and without guarantee.
