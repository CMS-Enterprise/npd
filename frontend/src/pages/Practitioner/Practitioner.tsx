import { Alert, Button } from "@cmsgov/design-system"
import classNames from "classnames"
import { useState, useEffect } from "react"
import { useTranslation } from "react-i18next"
import { Link, useLocation, useParams } from "react-router"
import { FeatureFlag } from "../../components/FeatureFlag"
import { LoadingIndicator } from "../../components/LoadingIndicator"
import {
  PractitionerPresenter,
  FullPractitionerPresenter,
} from "../../presenters/PractitionerPresenter"
import {
  usePractitionerAPI,
  useFullPractitionerAPI,
} from "../../state/requests/practitioners"
import layout from "../Layout.module.css"
import styles from "./Practitioner.module.css"
import React from "react"
import { FeedbackForm } from "../../components/forms/feedback/FeedbackForm"

const DetailRows = ({
  items,
}: {
  items: Array<{ label: string; value: string | null | undefined }>
}) => {
  return (
    <dl className={styles.detailsList}>
      {items.map((item) => (
        <div className={styles.detailRow} key={item.label}>
          <dt className={styles.detailLabel}>{item.label}</dt>
          <dd className={styles.detailValue}>{item.value || "—"}</dd>
        </div>
      ))}
    </dl>
  )
}

export const Practitioner = () => {
  const { t } = useTranslation()
  const { practitionerId } = useParams()
  const { data, error, isLoading } = usePractitionerAPI(practitionerId)
  const { fullData } = useFullPractitionerAPI(practitionerId)
  const location = useLocation()
  const searchUrl = location.state?.searchUrl

  const [isReportIssueOpen, setIsReportIssueOpen] = useState(false)

  useEffect(() => {
    document.body.classList.add("gray-bg")
    return () => document.body.classList.remove("gray-bg")
  }, [])

  if (isLoading) {
    return <LoadingIndicator />
  }

  if (typeof data === "undefined" || error) {
    return <p>API Error: {JSON.stringify(error)}</p>
  }

  const contentClass = classNames(layout.content, "ds-l-container")

  const practitioner = new PractitionerPresenter(data)
  const fullPractitioner = new FullPractitionerPresenter(fullData)
  const locations = fullPractitioner.locations
  const basicInformationItems = [
    {
      label: t("practitioners.detail.contact.npi"),
      value: practitioner.npi,
    },
    {
      label: t("practitioners.detail.contact.dateOfEnumeration"),
      value: practitioner.enumerationDate,
    },
    {
      label: t("practitioners.detail.contact.phone"),
      value: fullPractitioner.primaryPractice.phone || practitioner.phone,
    },
  ]

  return (
    <>
      <main className={classNames(contentClass, styles.pageShell)}>
        {searchUrl && (
          <a href={searchUrl} className={styles.backLink}>
            {t("practitioners.detail.header.search")}
          </a>
        )}
        <section className={classNames(styles.card, styles.summaryCard)}>
          <div className={styles.summaryMeta}>
            <h1
              role="heading"
              data-testid="practitioner-name"
              aria-level={1}
              className={styles.summaryHeading}
            >
              {practitioner.names[0] || ""}
            </h1>
            {practitioner.specialtySummary && (
              <div className={styles.taxonomy}>
                {practitioner.specialtySummary}
              </div>
            )}
            <div className={styles.verificationPill}>
              {t("practitioners.detail.verification.notVerified")}
            </div>
          </div>
        </section>

        <FeatureFlag inverse name="PRACTITIONER_LOOKUP_DETAILS">
          <Alert variation="warn" heading="Content not available">
            This content is not currently available.
          </Alert>
        </FeatureFlag>

        <FeatureFlag name="PRACTITIONER_LOOKUP_DETAILS">
          <div className={styles.contentGrid}>
            <section className={classNames(styles.card, styles.contactCard)}>
              <h2 className={styles.sectionTitle}>
                {t("practitioners.detail.contact.title")}
              </h2>
              <DetailRows items={basicInformationItems} />
            </section>

            <aside className={styles.sidebarColumn}>
              <div className={classNames(styles.card, styles.actionsCard)}>
                <h3 className={styles.actionsTitle}>
                  {t("practitioners.detail.actions.title")}
                </h3>
                <p className={styles.actionsDescription}>
                  {t("practitioners.detail.actions.description.before")}{" "}
                  <strong>
                    {t("practitioners.detail.actions.description.emphasis")}
                  </strong>
                  .
                </p>
                <Button
                  variation="solid"
                  className={styles.actionsButton}
                  disabled={true}
                >
                  {t("practitioners.detail.actions.claim")}
                </Button>
                <Button
                  variation="solid"
                  className={styles.actionsButton}
                  onClick={() => setIsReportIssueOpen(true)}
                >
                  {t("practitioners.detail.actions.report")}
                </Button>
              </div>
            </aside>

            <section className={classNames(styles.card, styles.locationsCard)}>
              <h2 className={styles.sectionTitle}>
                {t("practitioners.detail.locations.title")}
              </h2>
              <div className={styles.locationList}>
                {locations.length > 0 ? (
                  locations.map((location) => (
                    <div className={styles.locationItem} key={location.id}>
                      {(location.name || location.organizationName) && (
                        <div className={styles.locationTitle}>
                          {location.name || location.organizationName}
                          {location.organizationName &&
                            location.name &&
                            location.organizationName !== location.name && (
                              <div className={styles.locationOrganization}>
                                {location.organizationName}
                              </div>
                            )}
                          {location.organizationNpi && (
                            <span className={styles.locationTitleMeta}>
                              {" "}
                              ({t("practitioners.npi")}{" "}
                              {location.organizationId ? (
                                <Link
                                  to={`/organizations/${location.organizationId}`}
                                  className={styles.locationLink}
                                >
                                  {location.organizationNpi}
                                </Link>
                              ) : (
                                location.organizationNpi
                              )}
                              )
                            </span>
                          )}
                        </div>
                      )}
                      {location.address && (
                        <ul className={styles.locationAddressList}>
                          <li className={styles.locationAddress}>
                            {location.address}
                          </li>
                        </ul>
                      )}
                    </div>
                  ))
                ) : (
                  <div className={styles.locationEmpty}>—</div>
                )}
              </div>
            </section>
          </div>
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
