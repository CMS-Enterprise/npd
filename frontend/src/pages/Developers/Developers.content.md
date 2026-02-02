# Participating in the beta

This limited beta release provides a select group of early adopters the opportunity to explore our approach to achieving an interoperable National Provider Directory (NPD), provide feedback, and help shape the future of the initiative.

As we continue to develop the directory, you can expect performance improvements, API changes, and additional data incorporated into the data model to improve and streamline the directory output.

Please note the following:

- This site and API are available to you for testing purposes, the data should not be integrated into production systems
- Frequent updates and API changes are possible
- Feedback is encouraged

## Providing feedback

Feedback in all areas is welcome during the beta, including the following:

- The latest dataset
- API implementation
- Supporting documentation and resources

Feedback and questions may be submitted via [email](mailto:npd@cms.hhs.gov). Early adopters of the Health Tech Ecosystem can also share their feedback in the provider directory Slack channel. The CMS team may reach out to follow-up and ask for additional feedback.

Developers may also participate in our [open source project](#open-source-project).

# About the data

For the first time, CMS is aligning its internal provider data resources to establish a new dataset available through the National Provider Directory API.

The initial dataset combines data from NPPES, PECOS, CEHRT, and other CMS data sources.

The NPD will use an iterative approach to expand data sources over time. This will include additional internal provider, payer, claims, and network data, as well as incorporating external data from the industry.

# Accessing the data

## Overview

Developers can query and retrieve National Provider Directory data via a REST API. The API structure conforms to the HL7 Fast Healthcare Interoperability Resources (FHIR) standard and it returns JSON responses following the FHIR specification.

## Authentication

While it is not a long term goal for this API to require authentication for all requests, we currently require user accounts and [HTTP Basic Access Authentication](https://en.wikipedia.org/wiki/Basic_access_authentication) for all API requests.

To authenticate, each request should include a header field in the form of:

```
Authorization: Basic <credentials>
```

Where `<credentials>` is the Base64 encoded value of a string with the format “username:password”.

For example, if your username is `npd.user@cms.hhs.gov` and the password for your account is `toomanysecrets543`, then the un-encoded string is `npd.user@cms.hhs.gov:toomanysecrets543`, the base64 encoding is `bnBkLnVzZXJAY21zLmhocy5nb3Y6dG9vbWFueXNlY3JldHM1NDM=` and as part of a cURL request, that would look like:

```
curl -H "Authorization: Basic bnBkLnVzZXJAY21zLmhocy5nb3Y6dG9vbWFueXNlY3JldHM1NDM=" .../fhir/...
```

If you’re using the [developer sandbox](#developer-sandbox) to make requests while signed-in, your authentication will automatically pass through via a secure session cookie.

## Available endpoints

The initial beta release of the National Provider Directory API makes the following endpoints available. For a detailed description of the endpoints, query string parameters, and response bodies, please refer to the National Provider Directory [API documentation](/fhir/docs/redoc).

&nbsp;

| Endpoint                    | Description                                                                                                                                                                                                                                                                                                                                                                         |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| /fhir                       | lists all available endpoints                                                                                                                                                                                                                                                                                                                                                       |
| /fhir/metadata              | provides a CapabilityStatement resource with metadata about the API implementation                                                                                                                                                                                                                                                                                                  |
| /fhir/Endpoint/<id>         | lists URIs and addresses relevant to the exchange of information between entities (e.g. urls to other FHIR implementations), as well as details about those endpoints; supplying an id allows developers to retrieve a single endpoint record                                                                                                                                       |
| /fhir/Location/<id>         | lists locations at which healthcare services are provided, as well as details about those locations; supplying an id allows developers to retrieve a single location record                                                                                                                                                                                                         |
| /fhir/Organization/<id>     | lists both organizations that provide healthcare services (i.e. organizations having a Type 2 National Provider Identifier) and non-provider organizations that interact with the healthcare system (e.g. EHR vendors and data interoperability networks), as well as details about those organizations; supplying an id allows developers to retrieve a single organization record |
| /fhir/Practitioner/<id>     | lists individuals that provide healthcare services (I.e. individuals having a type 1 National Provider Identifier), as well as details about those practitioners; supplying an id allows developers to retrieve a single practitioner record                                                                                                                                        |
| /fhir/PractitionerRole/<id> | lists relationships between individuals that provide healthcare services, the organizations within which they provide healthcare services, the locations at which they practice, and the interoperability endpoints that pertain to those relationships; supplying an id allows developers to retrieve a single practitioner role record                                            |

# Developer sandbox

To explore the data in an interactive developer sandbox integrated with detailed documentation, please visit the National Provider Directory [Swagger documentation](/fhir/docs/).


# Open source project

The National Provider Directory team is taking an open source approach to the product development of this tool, operating as a [Tier 3 CMS Open Source Repository](https://github.com/DSACMS/repo-scaffolder/blob/main/tier3/README.md). We believe government software should be made in the open and be built and licensed such that anyone can download the code, run it themselves without paying money to third parties or using proprietary software, and use it as they will.

Although this project is led by a CMS team, we know that we can learn from a wide variety of communities, including those who will use or will be impacted by the tool, who are experts in technology, or who have experience with similar technologies deployed in other spaces. We are dedicated to creating forums for continuous conversation and feedback to help shape the design and development of the tool and welcome external contributions to our project.

To learn more, visit the [primary code repository](https://github.com/CMS-Enterprise/npd) on GitHub. Visit the [CMS Open Source Program Office](https://go.cms.gov/ospo) to learn more about their work.
