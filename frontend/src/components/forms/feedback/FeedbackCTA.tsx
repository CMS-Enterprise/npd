import { Button } from "@cmsgov/design-system"
import { useTranslation } from "react-i18next"
import classNames from "classnames"
import styles from "./FeedbackCTA.module.css"

type Props = {
  title: string
  subtitle: string
  onButtonClick: () => void
  isDisabled?: boolean
  className?: string
}

export const FeedbackCTA = ({
  subtitle: subtitleKey,
  onButtonClick,
  isDisabled = false,
  className,
}: Props) => {
  const { t } = useTranslation()
  const cardClass = classNames(styles.card, className)

  return (
    <div className={cardClass}>
      <h3 className="ds-text-heading--lg ds-u-margin-bottom--1">
        Help improve the directory
      </h3>
      <p className="ds-u-color--muted ds-u-margin-bottom--3">
        {t(subtitleKey)}
      </p>
      <Button variation="solid" onClick={onButtonClick} disabled={isDisabled}>
        Report an issue
      </Button>
    </div>
  )
}
