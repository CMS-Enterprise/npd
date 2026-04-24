import { useTranslation } from "react-i18next"

import layoutstyles from "../Layout.module.css"

export const ProvidersHeading = () => {
  const { t } = useTranslation()

  return (
    <section className="ds-l-container">
      <div className="ds-l-row">
        <div className="ds-l-col--12">
          <div className={layoutstyles.leader}>
            <div role="heading" aria-level={1} className={layoutstyles.title}>
              {t("providers.title")}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
