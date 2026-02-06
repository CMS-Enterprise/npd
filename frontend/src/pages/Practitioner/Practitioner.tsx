import { Alert } from "@cmsgov/design-system"
import classNames from "classnames"
import { useTranslation } from "react-i18next"
import { useParams } from "react-router"
import { FeatureFlag } from "../../components/FeatureFlag"
import { InfoItem } from "../../components/InfoItem"
import { LoadingIndicator } from "../../components/LoadingIndicator"
import { formatIdentifierType } from "../../helpers/formatters"
import { PractitionerPresenter } from "../../presenters/PractitionerPresenter"
import { usePractitionerAPI } from "../../state/requests/practitioners"
import layout from "../Layout.module.css"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "@cmsgov/design-system"

export const Practitioner = () => {
  const { t } = useTranslation()
  const { practitionerId } = useParams()
  const { data, error, isLoading } = usePractitionerAPI(practitionerId)

  if (isLoading) {
    return <LoadingIndicator />
  }

  if (typeof data === "undefined" || error) {
    return <p>API Error: {JSON.stringify(error)}</p>
  }

  const contentClass = classNames(layout.content, "ds-l-container")
  const bannerClass = classNames(layout.banner)

  const practitioner = new PractitionerPresenter(data)

  return (
    <>
      <section className={bannerClass}>
        <div className="ds-l-container">
          <div className="ds-l-row">
            <div className="ds-l-col--12">
              <div className={layout.leader}>
                <h1
                  role="heading"
                  data-testid="practitioner-name"
                  aria-level={1}
                  className={layout.title}
                >
                  {practitioner.name}
                </h1>
                <span
                  data-testid="practitioner-npi"
                  className={layout.subtitle}
                >
                  NPI: {practitioner.npi}
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>
      <main className={contentClass}>
        <FeatureFlag inverse name="PRACTITIONER_LOOKUP_DETAILS">
          <Alert variation="warn" heading="Content not available">
            This content is not currently available.
          </Alert>
        </FeatureFlag>

        <FeatureFlag name="PRACTITIONER_LOOKUP_DETAILS">
          <Alert heading={t("practitioners.detail.update.title")}>
            {t("practitioners.detail.update.subtitle")}{" "}
            <a href="#">{t("practitioners.detail.update.link")}</a>
          </Alert>

          <section className={layout.section}>
            <h2>{t("practitioners.detail.about.title")}</h2>
            <div className="ds-l-row">
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem
                  label={t("practitioners.detail.about.name")}
                  value={practitioner.name}
                />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem
                  label={t("practitioners.detail.about.gender")}
                  value={practitioner.gender}
                />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem
                  label={t("practitioners.detail.about.deceased")}
                  value={practitioner.isDeceased}
                />
              </div>
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem
                  label={t("practitioners.detail.about.status")}
                  value={practitioner.isActive}
                />
              </div>
            </div>
          </section>

          <section className={layout.section}>
            <h2>{t("practitioners.detail.contact.title")}</h2>
            <div className="ds-l-row">
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
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
              <div className="ds-l-col--12 ds-l-md-col--3 ds-u-margin-bottom--2">
                <InfoItem
                  label={t("practitioners.detail.contact.fax")}
                  value={practitioner.fax}
                />
              </div>
            </div>
          </section>

          <section className={layout.section}>
            <h2>{t("practitioners.detail.identifiers.title")}</h2>
            {/* TODO: look into modularizing table creation to reduce code duplication */}
            {practitioner.identifiers.length > 0 ? (
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>{t("practitioners.detail.identifiers.type")}</TableCell>
                    <TableCell>
                      {t("practitioners.detail.identifiers.number")}
                    </TableCell>
                    <TableCell>
                      {t("practitioners.detail.identifiers.details")}
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {practitioner.identifiers.map((identifier, index) => (
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
              <p className="ds-u-color--gray">
                {t("practitioners.detail.identifiers.fallback")}
              </p>
            )}
          </section>

          <section className={layout.section}>
            <h2>Taxonomy</h2>
            <p>[taxonomy information]</p>
          </section>

          <section className={layout.section}>
            <h2>Organization(s)</h2>
            <p>[endpoint information]</p>
          </section>
        </FeatureFlag>

        <div className="ds-u-margin-top--7"></div>
      </main>
    </>
  )
}
