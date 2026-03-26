import { Alert } from "@cmsgov/design-system"
import classNames from "classnames"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, useParams } from "react-router"
import { FeatureFlag } from "../../components/FeatureFlag"
import { InfoItem } from "../../components/InfoItem"
import { LoadingIndicator } from "../../components/LoadingIndicator"
import { DetailPageBanner } from "../../components/DetailPageBanner"
import { PractitionerPresenter } from "../../presenters/PractitionerPresenter"
import { usePractitionerAPI } from "../../state/requests/practitioners"
import layout from "../Layout.module.css"
import React from "react"
import { EndpointSection } from "../../components/detailSections/EndpointSection"
import { LocationSection } from "../../components/detailSections/LocationSection"
import { SectionWithContentOrFallback } from "../../components/detailSections/SectionWithContentOrFallback"
import { IdentifierSection } from "../../components/detailSections/IdentifierSection"
import { TaxonomySection } from "../../components/detailSections/TaxonomySection"
import { FeedbackCTA } from "../../components/forms/feedback/FeedbackCTA"
import { FeedbackForm } from "../../components/forms/feedback/FeedbackForm"

export const Practitioner = () => {
  const { t } = useTranslation()
  const { practitionerId } = useParams()
  const { data, error, isLoading } = usePractitionerAPI(practitionerId)
  const location = useLocation()
  const searchUrl = location.state?.searchUrl

  const [isReportIssueOpen, setIsReportIssueOpen] = useState(false)

  if (isLoading) {
    return <LoadingIndicator />
  }

  if (typeof data === "undefined" || error) {
    return <p>API Error: {JSON.stringify(error)}</p>
  }

  const contentClass = classNames(layout.content, "ds-l-container")

  const practitioner = new PractitionerPresenter(data)

  return (
    <>
      <DetailPageBanner
        title={practitioner.names[0] || ""}
        subtitle={`${t("practitioners.npi")}: ${practitioner.npi}`}
        pageType={t("practitioners.detail.header.type")}
        testIdPrefix="practitioner"
        backLink={
          searchUrl
            ? {
                label: t("practitioners.detail.header.search"),
                href: searchUrl,
              }
            : undefined
        }
      />
      <main className={contentClass}>
        <FeatureFlag inverse name="PRACTITIONER_LOOKUP_DETAILS">
          <Alert variation="warn" heading="Content not available">
            This content is not currently available.
          </Alert>
        </FeatureFlag>

        <FeatureFlag name="PRACTITIONER_LOOKUP_DETAILS">
          <section className={layout.section}>
            <div className="ds-l-row ds-u-align-items--start">
              <div className="ds-l-col--12 ds-l-md-col--8">
                <h2 className="ds-u-margin-top--0">
                  {t("practitioners.detail.about.title")}
                </h2>
                <div className="ds-l-row">
                  <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                    <InfoItem
                      label={t("practitioners.detail.about.name")}
                      value={practitioner.names.join("; ") || '—'}
                    />
                  </div>
                  <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                    <InfoItem
                      label={t("practitioners.detail.about.gender")}
                      value={practitioner.gender}
                    />
                  </div>
                </div>
              </div>
              <div className="ds-l-col--12 ds-l-md-col--4">
                <FeedbackCTA
                  subtitle={t("practitioners.detail.feedback.subtitle")}
                  onButtonClick={() => setIsReportIssueOpen(true)}
                />
              </div>
            </div>
          </section>

          <section className={layout.section}>
            <h2>{t("practitioners.detail.contact.title")}</h2>
            <div className="ds-l-row">
              <div
                className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2"
                style={{ whiteSpace: "pre-line " }}
              >
                <InfoItem
                  label={t("practitioners.detail.contact.address")}
                  value={practitioner.address}
                />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem
                  label={t("practitioners.detail.contact.phone")}
                  value={practitioner.phone}
                />
              </div>
            </div>
          </section>
          <IdentifierSection identifierData={practitioner.identifiers} />

          <TaxonomySection taxonomyData={practitioner.taxonomy} />

          <SectionWithContentOrFallback
            title={t("practitioners.detail.organizations.title")}
            fallback={t("practitioners.detail.organizations.notFound")}
            arrayData={Object.keys(practitioner.organizations)}
          >
            {Object.entries(practitioner.organizations).map(([id, obj]) => (
              <React.Fragment key={id}>
                <h3><a href={`/organizations/${id}`}>{`${obj.organization.name} (NPI: ${obj.organization.identifier?.filter((identifier) => (identifier.system = "http://terminology.hl7.org/NamingSystem/npi"))[0].value})`}</a></h3>
                <LocationSection
                  locationData={obj.locations.map((location) => {
                    return location
                  })}
                  subsection={true}
                />
                <EndpointSection
                  endpointData={obj.endpoints.map((endpoint) => {
                    return endpoint
                  })}
                  subsection={true}
                />
              </React.Fragment>
            ))}
          </SectionWithContentOrFallback>
        </FeatureFlag>

        <FeedbackForm
          isOpen={isReportIssueOpen}
          onExit={() => setIsReportIssueOpen(false)}
          presenterData={{
            recordName: practitioner.names[0] || "",
            recordId: practitionerId,
            npi: practitioner.npi,
          }}
        />

        <div className="ds-u-margin-top--7"></div>
      </main>
    </>
  )
}
