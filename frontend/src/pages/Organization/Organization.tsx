import { Alert, Button } from "@cmsgov/design-system"
import { FaRegComment } from "react-icons/fa"
import classNames from "classnames"
import { useState, useEffect } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, useParams } from "react-router"
import { FeatureFlag } from "../../components/FeatureFlag"
import { LoadingIndicator } from "../../components/LoadingIndicator"
import {
  OrganizationPresenter,
  FullOrganizationPresenter,
} from "../../presenters/OrganizationPresenter"
import {
  useOrganizationAPI,
  useFullOrganizationAPI,
} from "../../state/requests/organizations"
import { FeedbackForm } from "../../components/forms/feedback/FeedbackForm"
import styles from "./Organization.module.css"

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

export const Organization = () => {
  const { t } = useTranslation()
  const { organizationId } = useParams()
  const { data, isLoading } = useOrganizationAPI(organizationId)
  const { fullData, endpointDataLoading, locationDataLoading } =
    useFullOrganizationAPI(organizationId)
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

  const organization = new OrganizationPresenter(data!)
  const fullOrganization = new FullOrganizationPresenter(fullData!)

  const basicInfoItems = [
    {
      label: t("organizations.basicInfo.npi"),
      value: organization.npi,
    },
    {
      label: t("organizations.basicInfo.dateOfEnumeration"),
      value: organization.enumerationDate,
    },
    {
      label: t("organizations.basicInfo.phone"),
      value: organization.authorizedPhone,
    },
  ]

  const authorizedOfficialItems = [
    {
      label: t("organizations.authorizedOfficial.name"),
      value: organization.authorizedOfficial,
    },
    {
      label: t("organizations.authorizedOfficial.phone"),
      value: organization.authorizedPhone,
    },
  ]

  return (
    <>
      <main className={classNames("ds-l-container", styles.pageShell)}>
        {searchUrl && (
          <a href={searchUrl} className={styles.backLink}>
            {t("organizations.header.search")}
          </a>
        )}

        <section className={classNames(styles.card, styles.summaryCard)}>
          <div className={styles.summaryMeta}>
            <h1
              role="heading"
              data-testid="organization-name"
              aria-level={1}
              className={styles.summaryHeading}
            >
              {organization.name}
            </h1>
            {organization.npi && (
              <div data-testid="organization-npi" className={styles.npi}>
                {t("organizations.header.npi")}: {organization.npi}
              </div>
            )}
          </div>
        </section>

        <FeatureFlag inverse name="ORGANIZATION_LOOKUP_DETAILS">
          <Alert variation="warn" heading="Content not available">
            {t("organizations.unavailable")}
          </Alert>
        </FeatureFlag>

        <FeatureFlag name="ORGANIZATION_LOOKUP_DETAILS">
          <div className={styles.pageGrid}>
            <div className={styles.mainColumn}>
              <section className={styles.card}>
                <h2 className={styles.sectionTitle}>
                  {t("organizations.basicInfo.title")}
                </h2>
                <DetailRows items={basicInfoItems} />
              </section>

              {locationDataLoading ? (
                <section className={styles.card}>
                  <h2 className={styles.sectionTitle}>
                    {t("organizations.practiceLocations.title")}
                  </h2>
                  <LoadingIndicator />
                </section>
              ) : (
                <section className={styles.card}>
                  <h2 className={styles.sectionTitle}>
                    {t("organizations.practiceLocations.title")}
                  </h2>
                  {fullOrganization.locations.length === 0 ? (
                    <p className={styles.emptyState}>
                      {t("organizations.practiceLocations.empty")}
                    </p>
                  ) : (
                    <div className={styles.locationList}>
                      {fullOrganization.locations.map((loc) => {
                        const phone = loc.contact?.find(
                          (c) => c.system === "phone",
                        )?.value
                        return (
                          <div key={loc.id} className={styles.locationCard}>
                            {loc.name && (
                              <div className={styles.locationName}>
                                {loc.name}
                              </div>
                            )}
                            {loc.address && (
                              <div className={styles.locationDetail}>
                                {loc.address}
                              </div>
                            )}
                            {phone && (
                              <a
                                href={`tel:${phone}`}
                                className={styles.locationPhone}
                              >
                                {phone}
                              </a>
                            )}
                          </div>
                        )
                      })}
                    </div>
                  )}
                </section>
              )}

              <section className={styles.card}>
                <h2 className={styles.sectionTitle}>
                  {t("organizations.cmsNetworks.title")}
                </h2>
                <p className={styles.emptyState}>
                  {t("organizations.cmsNetworks.empty")}
                </p>
              </section>

              {endpointDataLoading ? (
                <section className={styles.card}>
                  <h2 className={styles.sectionTitle}>
                    {t("organizations.dataExchangeEndpoints.title")}
                  </h2>
                  <LoadingIndicator />
                </section>
              ) : (
                <section className={styles.card}>
                  <h2 className={styles.sectionTitle}>
                    {t("organizations.dataExchangeEndpoints.title")}
                  </h2>
                  {fullOrganization.endpoints.length === 0 ? (
                    <p className={styles.emptyState}>
                      {t("organizations.dataExchangeEndpoints.empty")}
                    </p>
                  ) : (
                    <div className={styles.endpointList}>
                      {fullOrganization.endpoints.map((ep) => (
                        <div key={ep.id} className={styles.endpointCard}>
                          {ep.name && (
                            <div className={styles.endpointName}>{ep.name}</div>
                          )}
                          <div className={styles.endpointMeta}>
                            <span className={styles.endpointMetaLabel}>
                              {t("organizations.dataExchangeEndpoints.type")}:
                            </span>{" "}
                            {ep.connectionType || "—"}
                          </div>
                          <div className={styles.endpointMeta}>
                            <span className={styles.endpointMetaLabel}>
                              {t("organizations.dataExchangeEndpoints.url")}:
                            </span>{" "}
                            {ep.address ? (
                              <a
                                href={ep.address}
                                className={styles.endpointUrl}
                                target="_blank"
                                rel="noreferrer"
                              >
                                {ep.address}
                              </a>
                            ) : (
                              "—"
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </section>
              )}
            </div>

            <aside className={styles.sidebarColumn}>
              <div className={styles.card}>
                <h3 className={styles.sectionTitle}>
                  {t("organizations.authorizedOfficial.title")}
                </h3>
                <DetailRows items={authorizedOfficialItems} />
              </div>

              <div className={classNames(styles.card, styles.actionsCard)}>
                <h3 className={styles.actionsTitle}>Actions</h3>

                <Button
                  variation="ghost"
                  className={classNames(
                    styles.actionsButton,
                    styles.reportButton,
                  )}
                  onClick={() => setIsReportIssueOpen(true)}
                >
                  <FaRegComment className={styles.actionButtonIcon} />
                  Report Issue with This Record
                </Button>
                <p className={styles.feedbackText}>
                  Found incorrect information? Let us know so we can update this
                  record.
                </p>
              </div>
            </aside>
          </div>
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
