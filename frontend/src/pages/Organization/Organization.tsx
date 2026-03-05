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
import styles from "./Organization.module.css"

export const Organization = () => {
  const { t } = useTranslation()
  const { organizationId } = useParams()
  const { data, isLoading } = useOrganizationAPI(organizationId)
  const location = useLocation()
  const searchUrl = location.state?.searchUrl

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
            <h2>{t("organizations.about.title")}</h2>
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

          <section className={layout.section}>
            <h2>{t("organizations.identifiers.title")}</h2>
            {organization.identifiers.length > 0 ? (
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>{t("organizations.identifiers.type")}</TableCell>
                    <TableCell>
                      {t("organizations.identifiers.number")}
                    </TableCell>
                    <TableCell>
                      {t("organizations.identifiers.details")}
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {organization.identifiers.map((identifier, index) => (
                    <TableRow key={index}>
                      <TableCell>{identifier.system}</TableCell>
                      <TableCell>{identifier.number}</TableCell>
                      <TableCell>{identifier.details}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p className="ds-u-color--gray">
                {t("organizations.identifiers.fallback")}
              </p>
            )}
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.taxonomy.title")}</h2>
            {organization.types.length > 0 ? (
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
            ) : (
              <p className={styles.emptyState}>
                {t("organizations.taxonomy.fallback")}
              </p>
            )}
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.endpoints")}</h2>
            <p className={styles.emptyState}>No endpoints available</p>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.locations")}</h2>
            <p className={styles.emptyState}>No locations available</p>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.practitioners")}</h2>
            <p className={styles.emptyState}>No practitioners available</p>
          </section>
        </FeatureFlag>

        <div className="ds-u-margin-top--7"></div>
      </main>
    </>
  )
}
