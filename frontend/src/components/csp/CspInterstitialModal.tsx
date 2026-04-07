import { Alert, Button, Dialog } from "@cmsgov/design-system"
import { useTranslation } from "react-i18next"

import styles from "./CspInterstitialModal.module.css"

interface CspInterstitialModalProps {
  isOpen: boolean
  providerName: string
  onContinue: () => void
  onCancel: () => void
}

export const CspInterstitialModal = ({
  isOpen,
  providerName,
  onContinue,
  onCancel,
}: CspInterstitialModalProps) => {
  const { t } = useTranslation()

  return (
    <Dialog
      isOpen={isOpen}
      onExit={onCancel}
      heading={t("csp.interstitial.heading", { provider: providerName })}
      size="wide"
      backdropClickExits={false}
    >
      <div className={styles.body}>
        <Alert variation="warn" className={styles.alert}>
          <p>
            <strong>{t("csp.interstitial.importantLabel")}</strong>{" "}
            {t("csp.interstitial.importantText")}
          </p>
        </Alert>

        <p className={styles.sectionHeading}>
          <strong>{t("csp.interstitial.needHeading")}</strong>
        </p>

        <ul className={styles.needList}>
          <li>{t("csp.interstitial.needId")}</li>
          <li>{t("csp.interstitial.needSsn")}</li>
          <li>{t("csp.interstitial.needPhoto")}</li>
        </ul>

        <p className={styles.paragraph}>
          {t("csp.interstitial.documentsReady")}
        </p>

        <p className={styles.paragraph}>
          {t("csp.interstitial.returnInfo", { provider: providerName })}
        </p>

        <div className={styles.privacyBox}>
          <p className={styles.privacyHeading}>
            <strong>{t("csp.interstitial.privacyHeading")}</strong>
          </p>
          <p className={styles.privacyText}>
            {t("csp.interstitial.privacyText", { provider: providerName })}
          </p>
        </div>

        <p className={styles.paragraph}>
          {t("csp.interstitial.actionPrompt", { provider: providerName })}
        </p>

        <div className={styles.actions}>
          <Button variation="ghost" onClick={onCancel}>
            {t("csp.interstitial.cancel")}
          </Button>
          <Button variation="solid" onClick={onContinue}>
            {t("csp.interstitial.continue")}
          </Button>
        </div>
      </div>
    </Dialog>
  )
}
