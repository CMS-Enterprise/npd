import { useTranslation } from "react-i18next"
import { Link } from "react-router"
import type { FHIROrganization } from "../../@types/fhir"
import { OrganizationPresenter } from "../../presenters/OrganizationPresenter"
import search from "../Search.module.css"

export const ListedOrganization = ({ data }: { data: FHIROrganization }) => {
  const { t } = useTranslation()
  const organization = new OrganizationPresenter(data)

  return (
    <div role="listitem" className="ds-u-border-top--1 ds-u-padding-y--2">
      <div className={search.entry}>
        <div className={search.head}>
          <Link
            className={search.name}
            to={`/organizations/${data.id}`}
            state={{ searchUrl: `/organizations/search${location.search}` }}
          >
            {organization.name}
          </Link>
          <span>
            <strong>NPI:</strong> {organization.npi}
          </span>
        </div>
        <div className="ds-l-row">
          <div className="ds-l-col--4 ds-m-col--6">
            <strong>{t("organizations.listing.taxonomy")}</strong>
            <br />
            {organization.types[0] ?? "---"}
          </div>
          <div
            className="ds-l-col--4 ds-m-col--6"
            style={{ whiteSpace: "pre-line" }}
          >
            <strong>{t("organizations.listing.location")}</strong>
            <br />
            {organization.address}
          </div>
        </div>
      </div>
    </div>
  )
}
