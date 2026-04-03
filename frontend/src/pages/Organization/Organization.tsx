import { Alert, Button } from "@cmsgov/design-system"
import { FaShieldAlt, FaRegComment } from "react-icons/fa"
import classNames from "classnames"
import { useState } from "react"
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
import { LocationSection } from "../../components/detailSections/LocationSection"
import { EndpointSection } from "../../components/detailSections/EndpointSection"
import { IdentifierSection } from "../../components/detailSections/IdentifierSection"
import { TaxonomySection } from "../../components/detailSections/TaxonomySection"
import { SectionWithContentOrFallback } from "../../components/detailSections/SectionWithContentOrFallback"
import { FeedbackForm } from "../../components/forms/feedback/FeedbackForm"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "@cmsgov/design-system"
import styles from "./Organization.module.css"

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

export const Organization = () => {
  const { t } = useTranslation()
  const { organizationId } = useParams()
  const { data, isLoading } = useOrganizationAPI(organizationId)
  const {
    fullData,
    endpointDataLoading,
    locationDataLoading,
    practitionerDataLoading,
  } = useFullOrganizationAPI(organizationId)
  const location = useLocation()
  const searchUrl = location.state?.searchUrl

  const [isReportIssueOpen, setIsReportIssueOpen] = useState(false)

  if (isLoading) {
    return <LoadingIndicator />
  }

  const organization = new OrganizationPresenter(data!)
  const fullOrganization = new FullOrganizationPresenter(fullData!)

  const aboutItems = [
    {
      label: t("organizations.about.otherNames"),
      value: organization.otherNames.join("; ") || null,
    },
    {
      label: t("organizations.about.parentOrganization"),
      value: null,
    },
  ]

  const contactItems = [
    {
      label: t("organizations.contact.address"),
      value: organization.address,
    },
    {
      label: t("organizations.contact.authorizedOfficial"),
      value: organization.authorizedOfficial,
    },
    {
      label: t("organizations.contact.authorizedOfficialPhone"),
      value: organization.authorizedPhone,
    },
  ]

  return (
    <>
      <main className="ds-l-container">
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
              {aboutItems.some((item) => item.value) && (
                <section className={styles.card}>
                  <h2 className={styles.sectionTitle}>
                    {t("organizations.about.title")}
                  </h2>
                  <DetailRows items={aboutItems} />
                </section>
              )}

              {contactItems.some((item) => item.value) && (
                <section className={styles.card}>
                  <h2 className={styles.sectionTitle}>
                    {t("organizations.contact.title")}
                  </h2>
                  <DetailRows items={contactItems} />
                </section>
              )}

              {organization.identifiers.length > 0 && (
                <section className={classNames(styles.card, styles.tableWrap)}>
                  <IdentifierSection
                    identifierData={organization.identifiers}
                  />
                </section>
              )}

              {organization.types.length > 0 && (
                <section className={classNames(styles.card, styles.tableWrap)}>
                  <TaxonomySection taxonomyData={organization.types} />
                </section>
              )}

              {endpointDataLoading ? (
                <section className={styles.card}>
                  <h2 className={styles.sectionTitle}>
                    {t("detailsections.endpoints.title")}
                  </h2>
                  <LoadingIndicator />
                </section>
              ) : (
                <section className={classNames(styles.card, styles.tableWrap)}>
                  <EndpointSection endpointData={fullOrganization.endpoints} />
                </section>
              )}

              {locationDataLoading ? (
                <section className={styles.card}>
                  <h2 className={styles.sectionTitle}>
                    {t("detailsections.locations.title")}
                  </h2>
                  <LoadingIndicator />
                </section>
              ) : (
                <section className={classNames(styles.card, styles.tableWrap)}>
                  <LocationSection locationData={fullOrganization.locations} />
                </section>
              )}

              {practitionerDataLoading ? (
                <section className={styles.card}>
                  <h2 className={styles.sectionTitle}>
                    {t("organizations.practitioners.title")}
                  </h2>
                  <LoadingIndicator />
                </section>
              ) : (
                <section className={classNames(styles.card, styles.tableWrap)}>
                  <SectionWithContentOrFallback
                    title={t("organizations.practitioners.title")}
                    fallback={t("organizations.practitioners.fallback")}
                    arrayData={fullOrganization.practitioners}
                  >
                    <Table data-testid="practitioner-table">
                      <TableHead>
                        <TableRow>
                          <TableCell>
                            {t("organizations.practitioners.name")}
                          </TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {fullOrganization.practitioners.map(
                          (practitioner, index) => (
                            <TableRow key={index}>
                              <TableCell>
                                <a
                                  data-testid={`practitioner-${index}`}
                                  href={`/practitioners/${practitioner.id}`}
                                >
                                  {practitioner.name}
                                </a>
                              </TableCell>
                            </TableRow>
                          ),
                        )}
                      </TableBody>
                    </Table>
                  </SectionWithContentOrFallback>
                </section>
              )}
            </div>

            <aside className={styles.sidebarColumn}>
              <div className={classNames(styles.card, styles.actionsCard)}>
                <h3 className={styles.actionsTitle}>Actions</h3>
                <Button variation="solid" className={styles.actionsButton}>
                  <FaShieldAlt className={styles.actionButtonIcon} />
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
                  <FaRegComment className={styles.actionButtonIcon} />
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
