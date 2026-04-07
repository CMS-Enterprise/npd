import classNames from "classnames"
import { useState } from "react"
import { useTranslation } from "react-i18next"

import { CspInterstitialModal } from "../../components/csp/CspInterstitialModal"
import { IdentityProviderCard } from "../../components/csp/IdentityProviderCard"
import idMeLogo from "../../assets/idme-logo.svg"
import { initiateIdMeLogin } from "../../state/cspAuth"

import styles from "./CspLogin.module.css"

export const CspLogin = () => {
  const { t } = useTranslation()
  const [showInterstitial, setShowInterstitial] = useState(false)

  const handleIdMeSelect = () => {
    setShowInterstitial(true)
  }

  const handleContinue = () => {
    // PLACEHOLDER: In production, this would redirect to ID.me OAuth authorization URL
    initiateIdMeLogin()
    setShowInterstitial(false)
  }

  const handleCancel = () => {
    setShowInterstitial(false)
  }

  return (
    <main className={classNames(styles.main)}>
      <div className="ds-l-container">
        <div className={styles.content}>
          <h1 className={styles.heading}>{t("csp.login.title")}</h1>

          <p className={styles.description}>{t("csp.login.description")}</p>

          <div className={styles.providerList}>
            <IdentityProviderCard
              logo={idMeLogo}
              logoAlt={t("csp.idme.logoAlt")}
              name={t("csp.idme.name")}
              description={t("csp.idme.description")}
              onSelect={handleIdMeSelect}
              testId="idme-provider-card"
            />
          </div>
        </div>
      </div>

      <CspInterstitialModal
        isOpen={showInterstitial}
        providerName={t("csp.idme.name")}
        onContinue={handleContinue}
        onCancel={handleCancel}
      />
    </main>
  )
}
