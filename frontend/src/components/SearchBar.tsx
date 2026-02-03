import { Button } from "@cmsgov/design-system"
import type { FormEvent, ChangeEvent } from "react"
import { useTranslation } from "react-i18next"
import classNames from "classnames"
import search from "../Search.module.css"

type Props = {
  value: string
  onChange: (value: string) => void
  onSearch: (query: string) => void
  labelKey: string
  buttonTextKey: string
  isLoading?: boolean
  isBackgroundLoading?: boolean
  className?: string
}

export const SearchBar = ({
  value,
  onChange,
  onSearch,
  labelKey,
  buttonTextKey,
  isLoading = false,
  isBackgroundLoading = false,
  className,
}: Props) => {
  const { t } = useTranslation()
  const inputClass = classNames(search.input, className)

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    onSearch(value)
  }

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>): void => {
    onChange(e.target.value)
  }

  const showLoadingState = isLoading && !isBackgroundLoading
  const isDisabled = value.length < 1 || showLoadingState

  return (
    <div className="ds-l-row">
      <div className="ds-l-col--12 ds-u-padding-bottom--4">
        <form onSubmit={handleSubmit}>
          <div className="ds-u-clearfix">
            <label className="ds-c-label" htmlFor="query">
              {t(labelKey)}
            </label>
            <div className={inputClass}>
              <input
                className="ds-c-field"
                type="text"
                name="query"
                id="query"
                value={value}
                onChange={handleInputChange}
              />
              <Button type="submit" variation="solid" disabled={isDisabled}>
                {showLoadingState ? t("search.searching") : t(buttonTextKey)}
              </Button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
