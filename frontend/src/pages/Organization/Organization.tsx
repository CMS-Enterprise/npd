import {
  Alert,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "@cmsgov/design-system"

import { useOrganizationAPI } from "../../state/requests/organizations"
import { OrganizationPresenter } from "../../presenters/OrganizationPresenter"

import classNames from "classnames"
import { useTranslation } from "react-i18next"
import { useLocation, useParams } from "react-router"
import { DetailPageBanner } from "../../components/DetailPageBanner"
import { FeatureFlag } from "../../components/FeatureFlag"
import { InfoItem } from "../../components/InfoItem"
import { LoadingIndicator } from "../../components/LoadingIndicator"
import layout from "../Layout.module.css"
import { LocationSection } from "../../components/detailSections/LocationSection"
import { EndpointSection } from "../../components/detailSections/EndpointSection"
import { SectionWithContentOrFallback } from "../../components/detailSections/SectionWithContentOrFallback"
import { IdentifierSection } from "../../components/detailSections/IdentifierSection"
import { FeedbackCTA } from "../../components/forms/feedback/FeedbackCTA"
import { useState } from "react"
import { FeedbackForm } from "../../components/forms/feedback/FeedbackForm"

export const Organization = () => {
  const { t } = useTranslation()
  const { organizationId } = useParams()
  const { data, isLoading } = useOrganizationAPI(organizationId)
  const location = useLocation()
  const searchUrl = location.state?.searchUrl

  const [isReportIssueOpen, setIsReportIssueOpen] = useState(false)

  if (isLoading) {
    return <LoadingIndicator />
  }

  const contentClass = classNames(layout.content, "ds-l-container")

  const organization = new OrganizationPresenter(data!)

  return (
    <>
      <DetailPageBanner
        title={organization.name}
        subtitle={`${t("organizations.header.npi")}: ${organization.npi}`}
        pageType={t("organizations.header.title")}
        testIdPrefix="organization"
        backLink={
          searchUrl
            ? { label: t("organizations.header.search"), href: searchUrl }
            : undefined
        }
      />
      <main className={contentClass}>
        <FeatureFlag inverse name="ORGANIZATION_LOOKUP_DETAILS">
          <Alert variation="warn" heading="Content not available">
            {t("organizations.unavailable")}
          </Alert>
        </FeatureFlag>

        <FeatureFlag name="ORGANIZATION_LOOKUP_DETAILS">
          <section className={layout.section}>
            <div className="ds-l-row ds-u-align-items--start">
              <div className="ds-l-col--12 ds-l-md-col--8">
                <h2 className="ds-u-margin-top--0">
                  {t("organizations.about.title")}
                </h2>
                <div className="ds-l-row">
                  <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                    <InfoItem
                      label={t("organizations.about.otherNames")}
                      value={organization.name}
                    />
                  </div>
                  <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                    <InfoItem
                      label={t("organizations.about.type")}
                      value={organization.types[0]}
                    />
                  </div>
                  <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                    <InfoItem
                      label={t("organizations.about.parentOrganization")}
                      value={null}
                    />
                  </div>
                </div>
              </div>

              <div
                className={classNames(
                  "ds-l-col--12 ds-l-md-col--4",
                  layout.feedbackCtaColumn,
                )}
              >
                <FeedbackCTA
                  subtitle={t("practitioners.detail.feedback.subtitle")}
                  onButtonClick={() => setIsReportIssueOpen(true)}
                />
              </div>
            </div>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.contact.title")}</h2>
            <div className="ds-l-row">
              <div
                className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2"
                style={{ whiteSpace: "pre-line" }}
              >
                <InfoItem
                  label={t("organizations.contact.address")}
                  value={organization.address}
                />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                <InfoItem
                  label={t("organizations.contact.authorizedOfficial")}
                  value={organization.authorizedOfficial}
                />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                <InfoItem
                  label={t("organizations.contact.authorizedOfficialPhone")}
                  value={organization.authorizedPhone}
                />
              </div>
            </div>
          </section>
          <IdentifierSection identifierData={organization.identifiers} />

          <SectionWithContentOrFallback
            title={t("organizations.taxonomy.title")}
            fallback={t("organizations.taxonomy.fallback")}
            arrayData={organization.types}
          >
            <div className="ds-l-row">
              <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                <InfoItem
                  label={t("organizations.taxonomy.primary")}
                  value={organization.types[0]}
                />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                <InfoItem
                  label={t("organizations.taxonomy.secondary")}
                  value={organization.types[1]}
                />
              </div>
            </div>
          </SectionWithContentOrFallback>

          <EndpointSection endpointData={organization.endpoints} />

          <LocationSection locationData={organization.locations} />

          <section className={layout.section}>
            <h2>{t("organizations.practitioners.title")}</h2>
            {organization.practitioners.length > 0 ? (
              <Table data-testid="practitioner-table">
                <TableHead>
                  <TableRow>
                    <TableCell>
                      {t("organizations.practitioners.name")}
                    </TableCell>
                    <TableCell>
                      {t("organizations.practitioners.taxonomy")}
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {organization.practitioners.map((practitioner, index) => (
                    <TableRow key={index}>
                      <TableCell>{practitioner.name}</TableCell>
                      <TableCell>{practitioner.taxonomy}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p className="ds-u-color--gray">
                {t("organizations.practitioners.fallback")}
              </p>
            )}
          </section>
        </FeatureFlag>

        <FeedbackForm
          isOpen={isReportIssueOpen}
          onExit={() => setIsReportIssueOpen(false)}
          presenterData={{
            recordName: organization.name,
            recordId: organizationId,
            npi: organization.npi,
          }}
        />

        <div className="ds-u-margin-top--7"></div>
      </main>
    </>
  )
}
