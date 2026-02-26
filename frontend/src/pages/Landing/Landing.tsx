import { Alert, Badge, Button } from "@cmsgov/design-system"
import classNames from "classnames"
import { useTranslation } from "react-i18next"

import { NpdMarkdown } from "../../components/markdown/NpdMarkdown"

import content from "./Landing.content.md?raw"
import alertContent from "./LandingAlert.content.md?raw"

import styles from "./Landing.module.css"

export const Landing = () => {
  const { t } = useTranslation()

  const secondaryClasses = classNames(
    styles.secondaryContent,
    "d-u-measure--base",
  )

  return (
    <>
      <section className={styles.hero}>
        <div className="ds-l-container">
          <div className={styles.heroSpacing}></div>
          <div className={styles.heroBody}>
            <div className="ds-l-row">
              <div className="ds-l-col--12">
                <Badge variation="info" className={styles.heroBadge}>
                  {t("landing.badge")}
                </Badge>

                <h1>{t("landing.title")}</h1>
                <p className={styles.tagline}>{t("landing.tagline")}</p>

                <div className={styles.primaryActions}>
                  <Button variation="solid" href="/developers">
                    {t("landing.links.developers")}
                  </Button>
                  <Button variation="solid" href="/search">
                    {t("landing.links.search")}
                  </Button>
                </div>
              </div>
            </div>
          </div>
          <div className={styles.heroSpacing}></div>
        </div>
      </section>

      <section className="ds-l-container">
        <div className="ds-l-row">
          <div className="ds-l-col--8 ds-s-col--12">
            <div className={styles.secondary}>
              <Alert heading={t("landing.beta.heading")}>
                <NpdMarkdown content={alertContent} />
              </Alert>

              <div className={secondaryClasses}>
                <NpdMarkdown content={content} />
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  )
}
