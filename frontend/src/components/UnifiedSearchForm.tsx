import type { FormEvent, ChangeEvent } from "react"
import { Alert, Button } from "@cmsgov/design-system"
import { useTranslation } from "react-i18next"
import styles from "./UnifiedSearchForm.module.css"

type Props = {
  values: UnifiedSearchParams
  onChange: (values: UnifiedSearchParams) => void
  onSearch: (values: UnifiedSearchParams) => void
  onClear: () => void
  isLoading?: boolean
}

export const UnifiedSearchForm = ({
  values,
  onChange,
  onSearch,
  onClear,
  isLoading = false,
}: Props) => {
  const { t } = useTranslation()

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    onSearch(values)
  }

  const handleFieldChange =
    (field: keyof UnifiedSearchParams) =>
    (e: ChangeEvent<HTMLInputElement>) => {
      onChange({ ...values, [field]: e.target.value })
    }

  const canSearch = !!(
    values.providerName ||
    values.organizationName ||
    values.npi
  )
  const showLocationHint = !!values.location && !canSearch

  return (
    <form onSubmit={handleSubmit}>
      <div className="ds-l-row ds-u-margin-top--2">
        <div className="ds-l-col--6">
          <label className="ds-c-label" htmlFor="provider-name">
            {t("search.unified.providerNameLabel")}
          </label>
          <input
            className="ds-c-field"
            type="text"
            id="provider-name"
            name="provider_name"
            placeholder={t("search.unified.providerNamePlaceholder")}
            value={values.providerName || ""}
            onChange={handleFieldChange("providerName")}
          />
        </div>
        <div className="ds-l-col--6">
          <label className="ds-c-label" htmlFor="organization-name">
            {t("search.unified.organizationLabel")}
          </label>
          <input
            className="ds-c-field"
            type="text"
            id="organization-name"
            name="organization_name"
            placeholder={t("search.unified.organizationPlaceholder")}
            value={values.organizationName || ""}
            onChange={handleFieldChange("organizationName")}
          />
        </div>
      </div>

      <div className="ds-l-row ds-u-margin-top--2">
        <div className="ds-l-col--6">
          <label className="ds-c-label" htmlFor="npi-number">
            {t("search.unified.npiLabel")}
          </label>
          <input
            className="ds-c-field"
            type="text"
            id="npi-number"
            name="npi"
            placeholder={t("search.unified.npiPlaceholder")}
            value={values.npi || ""}
            onChange={handleFieldChange("npi")}
            maxLength={10}
            inputMode="numeric"
          />
        </div>
        <div className="ds-l-col--6">
          <label className="ds-c-label" htmlFor="location">
            {t("search.unified.locationLabel")}
          </label>
          <input
            className="ds-c-field"
            type="text"
            id="location"
            name="location"
            placeholder={t("search.unified.locationPlaceholder")}
            value={values.location || ""}
            onChange={handleFieldChange("location")}
          />
        </div>
      </div>

      {showLocationHint && (
        <div className="ds-u-margin-top--2">
          <Alert variation="warn" hideIcon>
            {t("search.unified.locationHint")}
          </Alert>
        </div>
      )}

      <div className="ds-l-row ds-u-margin-top--3">
        <div
          className={`ds-l-col--12 ds-u-display--flex ds-u-align-items--center ${styles.actionsRow}`}
        >
          <Button
            type="submit"
            variation="solid"
            disabled={!canSearch || isLoading}
          >
            {isLoading
              ? t("search.searching")
              : t("search.unified.searchButton")}
          </Button>
          <Button
            type="button"
            variation="ghost"
            onClick={onClear}
            className={`ds-u-margin-left--2 ${styles.clearButton}`}
          >
            {t("search.unified.clearButton")}
          </Button>
        </div>
      </div>
    </form>
  )
}
