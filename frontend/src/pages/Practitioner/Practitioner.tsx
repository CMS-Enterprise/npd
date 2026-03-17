import classNames from "classnames"
import { useState } from "react"
import { useTranslation } from "react-i18next"
import { useLocation, useParams } from "react-router"
import { FeatureFlag } from "../../components/FeatureFlag"
import { InfoItem } from "../../components/InfoItem"
import { LoadingIndicator } from "../../components/LoadingIndicator"
import { DetailPageBanner } from "../../components/DetailPageBanner"
import { FeedbackCTA } from "../../components/forms/feedback/FeedbackCTA"
import { FeedbackForm } from "../../components/forms/feedback/FeedbackForm"
import { PractitionerPresenter } from "../../presenters/PractitionerPresenter"
import { usePractitionerAPI } from "../../state/requests/practitioners"
import layout from "../Layout.module.css"

import {
  Alert,
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
        title={practitioner.name}
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
                      value={practitioner.name}
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
                  subtitle="Let us know if you see any problems with this provider record."
                  onButtonClick={() => setIsReportIssueOpen(true)}
                />
              </div>
            </div>
          </section>

          <section className={layout.section}>
            <h2 className="ds-u-margin-top--4">
              {t("practitioners.detail.contact.title")}
            </h2>
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
                    <TableCell>
                      {t("practitioners.detail.identifiers.type")}
                    </TableCell>
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
                      <TableCell>{identifier.system}</TableCell>
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
            <h2>{t("practitioners.detail.taxonomy.title")}</h2>
            {practitioner.taxonomy.length > 0 ? (
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>
                      {t("practitioners.detail.taxonomy.state")}
                    </TableCell>
                    <TableCell>
                      {t("practitioners.detail.taxonomy.licenseNumber")}
                    </TableCell>
                    <TableCell>
                      {t("practitioners.detail.taxonomy.taxonomy")}
                    </TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {practitioner.taxonomy.map((taxonomy, index) => (
                    <TableRow key={index}>
                      <TableCell>{taxonomy.state}</TableCell>
                      <TableCell>{taxonomy.licenseNumber}</TableCell>
                      <TableCell>{taxonomy.displayCode}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            ) : (
              <p className="ds-u-color--gray">
                {t("practitioners.detail.taxonomy.fallback")}
              </p>
            )}
          </section>

          <section className={layout.section}>
            <h2>Organization(s)</h2>
            <p>[endpoint information]</p>
          </section>
        </FeatureFlag>

        <FeedbackForm
          isOpen={isReportIssueOpen}
          onExit={() => setIsReportIssueOpen(false)}
          presenterData={{
            recordName: practitioner.name,
          }}
        />

        <div className="ds-u-margin-top--7" />
      </main>
    </>
  )
}
