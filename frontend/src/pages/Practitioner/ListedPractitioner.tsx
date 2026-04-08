import { useQuery } from "@tanstack/react-query"
import { useTranslation } from "react-i18next"
import { Link } from "react-router"
import { FaUser } from "react-icons/fa"
import search from "../Search.module.css"
import { PractitionerPresenter } from "../../presenters/PractitionerPresenter"
import type { FHIRPractitioner } from "../../@types/fhir"
import { fetchPractitioner } from "../../state/requests/practitioners"
import { fetchPractitionerRoles } from "../../state/requests/practitionerrole"

type Props = {
  data: FHIRPractitioner
  organizationName?: string
  organizationId?: string | null
  taxonomyText?: string
  npiOverride?: string | null
  searchUrl?: string
}

export const ListedPractitioner = ({
  data,
  organizationName,
  organizationId,
  taxonomyText,
  npiOverride,
  searchUrl,
}: Props) => {
  const { t } = useTranslation()
  const practitionerId = data.id ?? null
  const initialPractitioner = new PractitionerPresenter(data)
  const needsPractitionerDetails =
    !!practitionerId &&
    (!initialPractitioner.npi ||
      !initialPractitioner.address ||
      !initialPractitioner.phone ||
      (!taxonomyText && initialPractitioner.taxonomy.length === 0))
  const { data: hydratedPractitioner } = useQuery<FHIRPractitioner>({
    queryKey: ["listed-practitioner", practitionerId],
    queryFn: ({ signal }) => fetchPractitioner(practitionerId!, signal),
    enabled: needsPractitionerDetails,
  })
  const effectivePractitionerData = hydratedPractitioner ?? data
  const practitioner = new PractitionerPresenter(effectivePractitionerData)
  const resolvedNpi = npiOverride ?? practitioner.npi
  const taxonomy =
    taxonomyText ??
    practitioner.taxonomy
      .map((item) => item.display)
      .slice(0, 5)
      .join(", ")
  const { data: practitionerRoles } = useQuery({
    queryKey: ["listed-practitioner-roles", resolvedNpi],
    queryFn: ({ signal }) =>
      fetchPractitionerRoles({
        practitionerNPI: resolvedNpi ?? undefined,
        signal,
      }),
    enabled: !!resolvedNpi && (!organizationName || !organizationId),
  })
  const roleOrganizations = Array.from(
    new Map(
      (practitionerRoles?.results.entry ?? [])
        .map((entry) => entry?.resource.organization)
        .filter(
          (organization) =>
            !!organization?.display && !!organization?.reference,
        )
        .map((organization) => [
          organization!.reference,
          {
            id: organization!.reference.split("/").pop() ?? null,
            name: organization!.display ?? "---",
          },
        ]),
    ).values(),
  )
  const resolvedOrganizationId =
    organizationId ?? roleOrganizations[0]?.id ?? null
  const resolvedOrganizationName =
    organizationName ?? roleOrganizations[0]?.name
  const detailUrl = practitionerId ? `/practitioners/${practitionerId}` : null
  const backLink = searchUrl ?? `/practitioners/search${location.search}`

  return (
    <div role="listitem" className="ds-u-border-top--1 ds-u-padding-y--2">
      <div className={search.entry}>
        <div className={search.head}>
          <FaUser className={search.icon} size={18} aria-hidden="true" />
          <div className={search.titleBlock}>
            {detailUrl ? (
              <Link
                className={search.name}
                to={detailUrl}
                state={{ searchUrl: backLink }}
              >
                {practitioner.names[0]}
              </Link>
            ) : (
              <span className={search.name}>{practitioner.names[0]}</span>
            )}
          </div>
        </div>
        <div className={search.body}>
          <div className={search.field}>
            <div className={search.label}>{t("practitioners.npi")}</div>
            <div className={search.value}>{resolvedNpi ?? "---"}</div>
          </div>
          <div className={search.field}>
            <div className={search.label}>
              {t("search.unified.organizationLabel")}
            </div>
            <div className={search.value}>
              {resolvedOrganizationId ? (
                <Link
                  to={`/organizations/${resolvedOrganizationId}`}
                  state={{ searchUrl: backLink }}
                >
                  {resolvedOrganizationName ?? "---"}
                </Link>
              ) : (
                (resolvedOrganizationName ?? "---")
              )}
            </div>
          </div>
          <div className={search.field}>
            <div className={search.label}>
              {t("practitioners.listing.address")}
            </div>
            <div className={search.value}>{practitioner.address || "---"}</div>
          </div>
          <div className={search.field}>
            <div className={search.label}>
              {t("practitioners.detail.contact.phone")}
            </div>
            <div className={search.value}>{practitioner.phone || "---"}</div>
          </div>
          <div className={search.field}>
            <div className={search.label}>
              {t("practitioners.listing.taxonomy")}
            </div>
            <div className={search.value}>{taxonomy || "---"}</div>
          </div>
        </div>
        <div className={search.actions}>
          {detailUrl && (
            <Link
              className={search.actionButton}
              to={detailUrl}
              state={{ searchUrl: backLink }}
            >
              {t("search.unified.viewFullProfile")}
            </Link>
          )}
        </div>
      </div>
    </div>
  )
}
