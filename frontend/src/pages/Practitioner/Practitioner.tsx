import { Alert, Button } from "@cmsgov/design-system"
import classNames from "classnames"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, useParams } from "react-router"
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
import { IdentifierSection } from "../../components/detailSections/IdentifierSection"
import { TaxonomySection } from "../../components/detailSections/TaxonomySection"
import { FeedbackForm } from "../../components/forms/feedback/FeedbackForm"

const DetailRows = ({
  items,
}: {
  items: Array<{ label: string; value: string | null | undefined }>
}) => {
  const visibleItems = items.filter((item) => item.value)

  if (visibleItems.length === 0) {
    return null
  }

  return (
    <dl className={styles.detailsList}>
      {visibleItems.map((item) => (
        <div className={styles.detailRow} key={item.label}>
          <dt className={styles.detailLabel}>{item.label}</dt>
          <dd className={styles.detailValue}>{item.value}</dd>
        </div>
      ))}
    </dl>
  )
}

export const Practitioner = () => {
  const { t } = useTranslation()
  const { practitionerId } = useParams()
  const { data, error, isLoading } = usePractitionerAPI(practitionerId)
  const { fullData, fullDataLoading } = useFullPractitionerAPI(practitionerId)
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
  const fullPractitioner = new FullPractitionerPresenter(fullData)
  const organizations = fullPractitioner.organizationCards
  const contactItems = [
    {
      label: t("practitioners.detail.contact.organization"),
      value: fullPractitioner.primaryOrganizationName,
    },
    {
      label: t("practitioners.detail.contact.address"),
      value: practitioner.address,
    },
    {
      label: t("practitioners.detail.contact.phone"),
      value: practitioner.phone,
    },
    {
      label: t("practitioners.detail.contact.fax"),
      value: practitioner.fax,
    },
  ].filter((item) => item.value)

  return (
    <>
      <main className={contentClass}>
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
            {practitioner.primaryTaxonomy && (
              <div className={styles.taxonomy}>
                {practitioner.primaryTaxonomy}
              </div>
            )}
            {practitioner.npi && (
              <div data-testid="practitioner-npi" className={styles.npi}>
                {t("practitioners.npi")}: {practitioner.npi}
              </div>
            )}
          </div>
        </section>

        <FeatureFlag inverse name="PRACTITIONER_LOOKUP_DETAILS">
          <Alert variation="warn" heading="Content not available">
            This content is not currently available.
          </Alert>
        </FeatureFlag>

        <FeatureFlag name="PRACTITIONER_LOOKUP_DETAILS">
          <div className={styles.pageGrid}>
            <div className={styles.mainColumn}>
              {contactItems.length > 0 && (
                <section className={styles.card}>
                  <h2 className={styles.sectionTitle}>
                    {t("practitioners.detail.contact.title")}
                  </h2>
                  <DetailRows items={contactItems} />
                </section>
              )}

              {/* {practitioner.taxonomy.length > 0 && (
                <section className={classNames(styles.card, styles.tableWrap)}>
                  <TaxonomySection taxonomyData={practitioner.taxonomy} />
                </section>
              )} */}

              {practitioner.identifiers.length > 0 && (
                <section className={classNames(styles.card, styles.tableWrap)}>
                  <IdentifierSection
                    identifierData={practitioner.identifiers}
                  />
                </section>
              )}

              {fullDataLoading ? (
                <section className={styles.card}>
                  <h2 className={styles.sectionTitle}>
                    {t("practitioners.detail.organizations.title")}
                  </h2>
                  <LoadingIndicator />
                </section>
              ) : organizations.length > 0 ? (
                <section className={styles.card}>
                  <h2 className={styles.sectionTitle}>
                    {t("practitioners.detail.organizations.title")}
                  </h2>
                  {organizations.map((organization) => (
                    <div
                      className={styles.organizationCard}
                      key={organization.id}
                    >
                      <h3 className={styles.organizationTitle}>
                        <a href={`/organizations/${organization.id}`}>
                          {organization.name}
                        </a>
                      </h3>
                      {organization.npi && (
                        <div className={styles.organizationMeta}>
                          {t("practitioners.npi")}: {organization.npi}
                        </div>
                      )}

                      {organization.locations.length > 0 && (
                        <div className={styles.subsection}>
                          <h4 className={styles.subsectionTitle}>
                            {t("practitioners.detail.locations.title")}
                          </h4>
                          <div className={styles.stackedList}>
                            {organization.locations.map((location) => {
                              const contact = location.contact?.find(
                                (item) =>
                                  item.system === "phone" ||
                                  item.system === "fax",
                              )

                              return (
                                <div
                                  className={styles.stackedItem}
                                  key={location.id}
                                >
                                  {location.name && (
                                    <div className={styles.stackedItemTitle}>
                                      {location.name}
                                    </div>
                                  )}
                                  <DetailRows
                                    items={[
                                      {
                                        label: t(
                                          "practitioners.detail.locations.address",
                                        ),
                                        value: location.address,
                                      },
                                      {
                                        label:
                                          contact?.system === "fax"
                                            ? t(
                                                "practitioners.detail.contact.fax",
                                              )
                                            : t(
                                                "practitioners.detail.contact.phone",
                                              ),
                                        value: contact?.value,
                                      },
                                    ]}
                                  />
                                </div>
                              )
                            })}
                          </div>
                        </div>
                      )}

                      {organization.endpoints.length > 0 && (
                        <div className={styles.subsection}>
                          <h4 className={styles.subsectionTitle}>
                            {t("practitioners.detail.endpoints.title")}
                          </h4>
                          <div className={styles.stackedList}>
                            {organization.endpoints.map((endpoint) => (
                              <div
                                className={styles.stackedItem}
                                key={endpoint?.id}
                              >
                                <DetailRows
                                  items={[
                                    {
                                      label: t(
                                        "practitioners.detail.endpoints.connectionType",
                                      ),
                                      value: endpoint?.connectionType,
                                    },
                                    {
                                      label: t(
                                        "practitioners.detail.endpoints.address",
                                      ),
                                      value: endpoint?.address,
                                    },
                                  ]}
                                />
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </section>
              ) : null}
            </div>

            <aside className={styles.sidebarColumn}>
              <div className={classNames(styles.card, styles.actionsCard)}>
                <h3 className={styles.actionsTitle}>Actions</h3>
                <Button variation="solid" className={styles.actionsButton}>
                  This Is Me
                </Button>
                <p className={styles.actionsDescription}>
                  Claim this record to update your information. You'll be asked
                  to securely log in, then review and verify your record. Once
                  completed, your record will be <strong>IAL2 Verified</strong>.
                </p>
                <Button
                  variation="ghost"
                  className={classNames(
                    styles.actionsButton,
                    styles.reportButton,
                  )}
                  onClick={() => setIsReportIssueOpen(true)}
                >
                  Report Issue with This Record
                </Button>
              </div>
            </aside>
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
