import { Badge } from "@cmsgov/design-system"
import { useTranslation } from "react-i18next"

import styles from "./AuthCards.module.css"

const CheckIcon = () => (
  <svg
    width="20"
    height="20"
    viewBox="0 0 20 20"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <rect width="20" height="20" rx="3" fill="#0071BC" />
    <path d="M8 14.4L4 10.4L5.4 9L8 11.6L14.6 5L16 6.4L8 14.4Z" fill="white" />
  </svg>
)

type AuthCardProps = {
  title: string
  description: string
  features: string[]
  badge?: string
}

const AuthCard = ({ title, description, features, badge }: AuthCardProps) => {
  return (
    <div className={styles.card}>
      <div className={styles.cardHeader}>
        <h3 className={styles.cardTitle}>{title}</h3>
        {badge && (
          <Badge variation="info" className={styles.cardBadge}>
            {badge}
          </Badge>
        )}
      </div>
      <p className={styles.cardDescription}>{description}</p>
      <ul className={styles.featureList}>
        {features.map((feature) => (
          <li key={feature} className={styles.featureItem}>
            <CheckIcon />
            <span>{feature}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export const AuthCards = () => {
  const { t } = useTranslation()

  return (
    <div className={styles.cardGrid}>
      <AuthCard
        title={t("about.auth.idme.title")}
        description={t("about.auth.idme.description")}
        features={[
          t("about.auth.idme.feature1"),
          t("about.auth.idme.feature2"),
          t("about.auth.idme.feature3"),
        ]}
      />
      <AuthCard
        title={t("about.auth.clear.title")}
        description={t("about.auth.clear.description")}
        badge={t("about.auth.clear.badge")}
        features={[
          t("about.auth.clear.feature1"),
          t("about.auth.clear.feature2"),
          t("about.auth.clear.feature3"),
        ]}
      />
      <AuthCard
        title={t("about.auth.logingov.title")}
        description={t("about.auth.logingov.description")}
        badge={t("about.auth.logingov.badge")}
        features={[
          t("about.auth.logingov.feature1"),
          t("about.auth.logingov.feature2"),
          t("about.auth.logingov.feature3"),
        ]}
      />
    </div>
  )
}
