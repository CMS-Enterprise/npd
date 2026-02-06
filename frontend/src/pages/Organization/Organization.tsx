import {
  Alert,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "@cmsgov/design-system"

import {
  organizationAuthorizedOfficialSelector,
  organizationAuthorizedPhoneSelector,
  organizationIdentifiersSelector,
  organizationMailingAddressSelector,
  organizationNpiSelector,
  useOrganizationAPI,
} from "../../state/requests/organizations"

import classNames from "classnames"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router"
import { FeatureFlag } from "../../components/FeatureFlag"
import { InfoItem } from "../../components/InfoItem"
import { LoadingIndicator } from "../../components/LoadingIndicator"
import { formatIdentifierType } from "../../helpers/formatters"
import layout from "../Layout.module.css"
import styles from "./Organization.module.css"

export const Organization = () => {
  const { t } = useTranslation()
  const { organizationId } = useParams()
  const { data, isLoading } = useOrganizationAPI(organizationId)

  if (isLoading) {
    return <LoadingIndicator />
  }

  const contentClass = classNames(layout.content, "ds-l-container")
  const bannerClass = classNames(layout.banner, "banner")

  const npi = organizationNpiSelector(data)
  const mailingAddress = organizationMailingAddressSelector(data)
  const authorizedOfficial = organizationAuthorizedOfficialSelector(data)
  const authorizedPhone = organizationAuthorizedPhoneSelector(data)
  const identifiers = organizationIdentifiersSelector(data)

  return (
    <>
      <section className={bannerClass}>
        <div className="ds-l-container">
          <div className="ds-l-row">
            <div className="ds-l-col--12">
              <div className={layout.leader}>
                <span className={layout.subtitle}>
                  {t("organizations.title")}
                </span>
                <div role="heading" aria-level={1} className={layout.title}>
                  {data?.name}
                </div>
                <span className={layout.subtitle}>NPI: {npi}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
      <main className={contentClass}>
        <FeatureFlag inverse name="ORGANIZATION_LOOKUP_DETAILS">
          <Alert variation="warn" heading="Content not available">
            {t("organizations.unavailable")}
          </Alert>
        </FeatureFlag>

        <FeatureFlag name="ORGANIZATION_LOOKUP_DETAILS">
          <Alert heading={t("organizations.update.title")}>
            {t("organizations.update.subtitle")}{" "}
            <a href="#">{t("organizations.update.link")}</a>
          </Alert>

          <section className={layout.section}>
            <h2>{t("organizations.about")}</h2>
            <div className="ds-l-row">
              <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                <InfoItem label="Other name(s)" value={data?.name} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                <InfoItem label="Type" value="Provider Group" />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                <InfoItem label="Parent organization" value={null} />
              </div>
            </div>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.contact")}</h2>
            <div className="ds-l-row">
              <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                <InfoItem label="Mailing address" value={mailingAddress} />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                <InfoItem
                  label="Authorized official"
                  value={authorizedOfficial}
                />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--4 ds-u-margin-bottom--2">
                <InfoItem
                  label="Authorized official phone"
                  value={authorizedPhone}
                />
              </div>
            </div>
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.identifiers")}</h2>
            {/* TODO: look into modularizing table creation to reduce code duplication */}
            {identifiers.length > 0 ? (
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Type</TableCell>
                    <TableCell>Number</TableCell>
                    <TableCell>Details</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {identifiers.map((identifier, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        {formatIdentifierType(identifier.system ?? "Unknown")}
                      </TableCell>
                      <TableCell>{identifier.number}</TableCell>
                      <TableCell>{identifier.details}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p className="ds-u-color--gray">No identifiers available</p>
            )}
          </section>

          <section className={layout.section}>
            <h2>{t("organizations.taxonomy")}</h2>
            <p className={styles.emptyState}>No taxonomy available</p>
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
