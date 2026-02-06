# CMS National Provider Directory

- [CMS National Provider Directory](#cms-national-provider-directory)
  - [About the Project](#about-the-project)
    - [Problem](#problem)
    - [Main Challenges](#main-challenges)
      - [Planned Solution](#planned-solution)
    - [Project Vision](#project-vision)
    - [Agency Mission](#agency-mission)
    - [Team Mission](#team-mission)
  - [Core Team](#core-team)
  - [Repository Structure](#repository-structure)
- [Development and Software Delivery Lifecycle](#development-and-software-delivery-lifecycle)
  - [Project Setup and Development](#project-setup-and-development)
  - [Community](#community)
    - [Community Guidelines](#community-guidelines)
  - [Governance](#governance)
  - [Feedback](#feedback)
  - [Policies](#policies)
    - [Open Source Policy](#open-source-policy)
    - [Security and Responsible Disclosure Policy](#security-and-responsible-disclosure-policy)
    - [Software Bill of Materials (SBOM)](#software-bill-of-materials-sbom)
  - [Public domain](#public-domain)

## About the Project

### Problem

CMS maintains the country’s de facto provider directory because of the agency’s role in registering new doctors for a National Provider ID in the National Plan and Provider Enumeration System (NPPES), and because of the agency’s role in enrolling providers in Medicare, overseeing the State Medicaid programs, and running the Federally-facilitated marketplace.

Enrollment for Medicaid happens in the states, but for Medicare, the enrollment workflow happens in the Provider Enrollment, Chain, and Ownership System (PECOS). However, NPPES and PECOS data is often inaccurate and lacks key interoperability information needed by CMS and the industry. The Medicare enrollment process provides some validation of the information, but the process is done in multiple systems, partly performed by CMS and partly performed by regional Medicare Administrative Contractors (MACs).

Additionally, there are several paper forms (received by fax) involved in the process and proprietary solutions used by the MACs to validate the data before submitting it back to CMS. These processes are duplicative, ineffective, costly, and the improved information is not shared back with the industry.

The healthcare system has been begging for a single directory at CMS for decades and the cost to the larger healthcare industry of not having one is estimated at $2.76B a year.

### Main Challenges

* There is no reliable single source of truth for accurate provider information. CMS itself has at least five systems that manage provider information. The CMS NPPES system is the default directory used as a starter provider database for the industry, but due to data quality problems , it is branched and corrected over 5,000 times in the industry where updates are applied in silos.
* Provider directories across the industry are inaccurate, with manual validation done over the phone, or via fax or email.
* Due to duplicative places the provider has to update and the risk of fines from health plans, plans continually badger providers to update their information. Because each provider has to update ~20 systems monthly, the exercise is futile and there is lack of motivation to keep trying.
* Billing information and patient-facing information are consistently conflated within the ecosystem causing patients to try to visit mailing addresses, rather than practice addresses.
* Interoperability efforts desperately need a central repository of provider FHIR endpoints, but it does not currently exist.
* The health plan data that indicates which providers participate in each insurance plan is stored in different formats, is difficult to access, and is updated at different intervals. This results in patients being unable to access accurate information as they seek care, which means that patients cannot find plans with the specific providers they need, nor can they easily tell if a provider they want to see will be covered by their insurance.

#### Planned Solution

We are breaking the initial MVP work into two work streams: **Core Data Model** and **National Provider Directory**.

The Core Data Model workstream encompassess all of the incoming data pipelines from various CMS open data sources, internal-to-CMS data sources, and data provided by industry partners. The goal of the Core Data Model workstream is to layer and combine data from these sources to build as accurate of a representation of our nation's healthcare providers, healthcare providing organizations, and healthcare data networks as possible.

The National Provider Directory workstream focuses on exposing the key elements of the Core Data Model through a FHIR API and a user-friendly search interface.

Eventually, providers and organizations will be able to use the National Provider Directory to update their information as well.

### Project Vision

We envision a world where the provider experience at CMS is so seamless that it is a joy and a breeze for providers to keep their information up-to-date.

The CMS Provider Directory should be an authoritative and accurate source of provider information.

### Agency Mission

The Centers for Medicare and Medicaid Services (CMS) provides health coverage to more than 100 million people through Medicare, Medicaid, the Children’s Health Insurance Program, and the Health Insurance Marketplace. The CMS seeks to strengthen and modernize the Nation’s health care system, to provide access to high quality care and improved health at lower costs.

### Team Mission

We are a cross-functional team of product managers, designers, and software engineers, who are working together to improve the Provider experience at CMS.

## Core Team

A list of core team members responsible for the code and documentation in this repository can be found in [COMMUNITY.md](COMMUNITY.md).

## Repository Structure

This is the main repository for the National Provider Directory (NPD) workstream. You will find more information about each component in a README.md file within its respective directory.

- [backend](./backend/): FHIR Provider Directory API and directory browser
- [frontend](./frontend/): Directory browser React application
- [flyway](./flyway/): Database migrations
- [playwright](./playwright/): End-to-end test suite

The [CMS-Enterprise/npd_etl](https://github.com/CMS-Enterprise/npd_etl) project on GitHub, which is currently a private repository, provides data ingestion for this system.

# Development and Software Delivery Lifecycle

We are taking an iterative approach to the development of this project, starting first with an MVP and building additional functionality as we go.

## Project Setup and Development

**For more information on contributing, including notes on project setup and development, see: [CONTRIBUTING.md](./CONTRIBUTING.md).**

## Community

The NPD team is taking a community-first and open source approach to the product development of this tool. We believe government software should be made in the open and be built and licensed such that anyone can download the code, run it themselves without paying money to third parties or using proprietary software, and use it as they will.

We know that we can learn from a wide variety of communities, including those who will use or will be impacted by the tool, who are experts in technology, or who have experience with similar technologies deployed in other spaces. We are dedicated to creating forums for continuous conversation and feedback to help shape the design and development of the tool.

We also recognize capacity building as a key part of involving a diverse open source community. We are doing our best to use accessible language, provide technical and process documents, and offer support to community members with a wide variety of backgrounds and skillsets.

### Community Guidelines

Principles and guidelines for participating in our open source community are can be found in [COMMUNITY.md](COMMUNITY.md). Please read them before joining or starting a conversation in this repo or one of the channels listed below. All community members and participants are expected to adhere to the community guidelines and code of conduct when participating in community spaces including: code repositories, communication channels and venues, and events.

## Governance

Information about how the NPD community is governed may be found in [GOVERNANCE.md](GOVERNANCE.md).

## Feedback

If you have ideas for how we can improve or add to our capacity building efforts and methods for welcoming people into our community, please let us know at **opensource@cms.hhs.gov**.

If you would like to comment on the tool itself, please let us know by [filing an issue on our GitHub repository](https://github.com/CMS-Enterprise/npd/issues).

## Policies

### Open Source Policy

We adhere to the [CMS Open Source Policy](https://github.com/CMSGov/cms-open-source-policy). If you have any questions, just [shoot us an email at opensource@cms.hhs.gov](mailto:opensource@cms.hhs.gov).

### Security and Responsible Disclosure Policy

_Submit a vulnerability:_ Vulnerability reports can be submitted through [Bugcrowd](https://bugcrowd.com/cms-vdp). Reports may be submitted anonymously. If you share contact information, we will acknowledge receipt of your report within 3 business days.

For more information about our Security, Vulnerability, and Responsible Disclosure Policies, see [SECURITY.md](SECURITY.md).

### Software Bill of Materials (SBOM)

A Software Bill of Materials (SBOM) is a formal record containing the details and supply chain relationships of various components used in building software.

In the spirit of [Executive Order 14028 - Improving the Nation’s Cyber Security](https://www.gsa.gov/technology/it-contract-vehicles-and-purchasing-programs/information-technology-category/it-security/executive-order-14028), a SBOM for this repository is provided here: https://github.com/CMS-Enterprise/npd/network/dependencies.

For more information and resources about SBOMs, visit: https://www.cisa.gov/sbom.

## Public domain

This project is in the public domain within the United States, and copyright and related rights in the work worldwide are waived through the [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/) as indicated in [LICENSE](LICENSE).

All contributions to this project will be released under the CC0 dedication. By submitting a pull request or issue, you are agreeing to comply with this waiver of copyright interest.
 
   
 
