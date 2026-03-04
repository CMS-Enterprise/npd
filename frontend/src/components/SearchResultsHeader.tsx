import { PaginationCaption } from "./PaginationCaption"
import { Dropdown } from "@cmsgov/design-system"
import { useTranslation } from "react-i18next"
import type { DropdownChangeObject } from "@cmsgov/design-system"

type Props = {
  pagination: PaginationState
  options: {
    value: string
    label: string
  }[]
  value: string
  onChange: (value: string) => void
  inputLabel: string
  disabled?: boolean
}

export const SearchResultsHeader = ({
  pagination,
  options,
  value,
  onChange,
  inputLabel,
  disabled = false,
}: Props) => {
  const { t } = useTranslation()

  const handleSort = (change: DropdownChangeObject): void => {
    onChange(change.target.value)
  }

  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
      }}
    >
      <div style={{ display: "flex", gap: "8px" }}>
        <PaginationCaption pagination={pagination} />
      </div>
      <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
        {t(inputLabel)}
        <Dropdown
          label=""
          name="sort-dropdown-field"
          labelClassName="ds-u-display--none"
          options={options}
          value={value}
          onChange={handleSort}
          disabled={disabled}
        />
      </div>
    </div>
  )
}
