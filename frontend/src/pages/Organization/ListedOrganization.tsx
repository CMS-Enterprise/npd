import { useTranslation } from "react-i18next"
import { Link } from "react-router"
import type { FHIROrganization } from "../../@types/fhir"
import {
  organizationMailingAddressSelector,
  organizationNpiSelector,
} from "../../state/requests/organizations"
import search from "../Search.module.css"

export const ListedOrganization = ({ data }: { data: FHIROrganization }) => {
  const { t } = useTranslation()

  return (
    <div role="listitem" className="ds-u-border-top--1 ds-u-padding-y--2">
      <div className={search.entry}>
        <div className={search.head}>
          <Link className={search.name} to={`/organizations/${data.id}`}>
            {data.name}
          </Link>
          <span>
            <strong>NPI:</strong> {organizationNpiSelector(data)}
          </span>
        </div>
        <div className="ds-l-row">
          <div className="ds-l-col--4 ds-m-col--6">
            <strong>{t("organizations.listing.taxonomy")}</strong>
            <br />
            TBD
          </div>
          <div className="ds-l-col--4 ds-m-col--6">
            <strong>{t("organizations.listing.location")}</strong>
            <br />
            {organizationMailingAddressSelector(data)}
          </div>
        </div>
      </div>
    </div>
  )
}
