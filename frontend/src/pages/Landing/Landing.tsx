import { Button } from "@cmsgov/design-system"
import { Trans, useTranslation } from "react-i18next"

import styles from "./Landing.module.css"

export const Landing = () => {
  const { t } = useTranslation()

  return (
    <>
      <section className={styles.hero}>
        <div className={styles.heroLayout}>
          <div className={styles.heroCard}>
            <div className={styles.heroCardInner}>
              <p className={styles.heroCardText}>
                <Trans
                  i18nKey="landing.hero.cta"
                  components={{
                    trusted: <span className={styles.heroTrusted} />,
                  }}
                />
              </p>
              <Button
                variation="solid"
                href="/about"
                className={styles.heroCardButton}
                isAlternate
              >
                {t("landing.hero.aboutButton")}
              </Button>
            </div>
          </div>
          <div className={styles.heroRight}>
            <h1>{t("landing.title")}</h1>
            <p className={styles.tagline}>{t("landing.tagline")}</p>
          </div>
        </div>
      </section>

      <section className="ds-l-container">
        <div className={styles.missionSection}>
          <div className="ds-l-row">
            <div className="ds-l-col--4">
              <h2 className={styles.missionHeading}>
                {t("landing.mission.heading")}
              </h2>
            </div>
            <div className="ds-l-col--8">
              <p className={styles.missionBody}>{t("landing.mission.body1")}</p>
              <p className={styles.missionBody}>
                <Trans
                  i18nKey="landing.mission.body2"
                  components={{
                    bold: <strong />,
                  }}
                />
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className={styles.cardsSection}>
        <div className="ds-l-container">
          <div className="ds-l-row">
            <div className="ds-l-col--4">
              <div className={styles.card}>
                <h3>{t("landing.cards.explore.heading")}</h3>
                <p>{t("landing.cards.explore.description")}</p>
                <Button variation="solid" href="/search">
                  {t("landing.cards.explore.link")}
                </Button>
              </div>
            </div>
            <div className="ds-l-col--4">
              <div className={styles.card}>
                <h3>{t("landing.cards.providers.heading")}</h3>
                <p>{t("landing.cards.providers.description")}</p>
                <Button variation="solid" href="/providers">
                  {t("landing.cards.providers.link")}
                </Button>
              </div>
            </div>
            <div className="ds-l-col--4">
              <div className={styles.card}>
                <h3>{t("landing.cards.developers.heading")}</h3>
                <p>{t("landing.cards.developers.description")}</p>
                <Button variation="solid" href="/developers">
                  {t("landing.cards.developers.link")}
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
