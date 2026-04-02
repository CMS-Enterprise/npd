import { useTranslation } from "react-i18next"
import { Link } from "react-router"
import { FaHospital } from "react-icons/fa"
import { OrganizationPresenter } from "../../presenters/OrganizationPresenter"
import search from "../Search.module.css"
import type { FHIROrganization } from "../../@types/fhir"

export const ListedOrganization = ({ data }: { data: FHIROrganization }) => {
  const { t } = useTranslation()
  const organization = new OrganizationPresenter(data)
  const types = organization.types
    .map((taxonomy) => taxonomy.display)
    .slice(0, 5)
    .join(", ")

  return (
    <div role="listitem" className="ds-u-border-top--1 ds-u-padding-y--2">
      <div className={search.entry}>
        <div className={search.head}>
          <FaHospital className={search.icon} size={20} aria-hidden="true" />
          <div className={search.titleBlock}>
            <Link
              className={search.name}
              to={`/organizations/${data.id}`}
              state={{ searchUrl: `/organizations/search${location.search}` }}
            >
              {organization.name}
            </Link>
          </div>
        </div>
        <div className={search.body}>
          <div className={search.field}>
            <div className={search.label}>{t("organizations.header.npi")}</div>
            <div className={search.value}>{organization.npi || "---"}</div>
          </div>
          <div className={search.field}>
            <div className={search.label}>
              {t("organizations.listing.address")}
            </div>
            <div className={search.value}>{organization.address || "---"}</div>
          </div>
          <div className={search.field}>
            <div className={search.label}>{t("organizations.about.type")}</div>
            <div className={search.value}>{types || "---"}</div>
          </div>
        </div>
        <div className={search.actions}>
          <Link
            className={search.actionButton}
            to={`/organizations/${data.id}`}
            state={{ searchUrl: `/organizations/search${location.search}` }}
          >
            {t("search.unified.viewFullProfile")}
          </Link>
        </div>
      </div>
    </div>
  )
}
