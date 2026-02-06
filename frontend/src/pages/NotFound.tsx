import classNames from "classnames"

import { useTranslation } from "react-i18next"
import layout from "./Layout.module.css"

type LinkText = { href: string; text: string }

export const NotFound = () => {
  const { t } = useTranslation()

  const mainClasses = classNames(layout.main)

  console.log('t("errors.not_found.links")', t("errors.not_found.links"))

  return (
    <main className={mainClasses}>
      <div className="ds-base ds-l-container">
        <div className="ds-l-row">
          <div className="ds-l-lg-col--6 ds-l-md-col--8">
            <div className={layout.spacer}></div>
            <section className={layout.section}>
              <h2>{t("errors.not_found.title")}</h2>

              <p>{t("errors.not_found.message")}</p>

              <ul>
                {(
                  (t("errors.not_found.links", {
                    returnObjects: true,
                  }) as LinkText[]) || []
                ).map((link) => {
                  return (
                    <li key={link.href}>
                      <a href={link.href}>{link.text}</a>
                    </li>
                  )
                })}
              </ul>
            </section>

            <div className={layout.spacer}></div>
          </div>
        </div>
      </div>
    </main>
  )
}
