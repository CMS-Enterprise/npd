import { useTranslation } from "react-i18next"
import { Link } from "react-router"
import type { FHIRPractitioner } from "../../@types/fhir"
import search from "../Search.module.css"
import { PractitionerPresenter } from "../../presenters/PractitionerPresenter"

export const ListedPractitioner = ({ data }: { data: FHIRPractitioner }) => {
  const { t } = useTranslation()
  const practitioner = new PractitionerPresenter(data)

  return (
    <div role="listitem" className="ds-u-border-top--1 ds-u-padding-y--2">
      <div className={search.entry}>
        <div className={search.head}>
          <Link className={search.name} to={`/practitioners/${data.id}`}>
            {practitioner.name}
          </Link>
          <span>
            <strong>NPI:</strong> {practitioner.npi}
          </span>
        </div>
        <div className="ds-l-row">
          <div className="ds-l-col--4 ds-m-col--6">
            <strong>{t("practitioners.listing.taxonomy")}</strong>
            <br />
            TBD
          </div>
          <div className="ds-l-col--4 ds-m-col--6">
            <strong>{t("practitioners.listing.location")}</strong>
            <br />
              {practitioner.address}
          </div>
        </div>
      </div>
    </div>
  )
}
