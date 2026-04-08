import { SkipNav } from "@cmsgov/design-system"
import { useTranslation } from "react-i18next"

import classNames from "classnames"

import { NpdMarkdown } from "../../components/markdown/NpdMarkdown"
import { ProvidersHeading } from "./ProvidersHeading"

import layoutstyles from "../Layout.module.css"

import content from "./Providers.content.md?raw"

export const Providers = () => {
  const { t } = useTranslation()
  const contentClass = classNames(layoutstyles.content, "ds-l-container")

  return (
    <>
      <ProvidersHeading />
      <main className={contentClass}>
        <SkipNav href="#content" />
        <div className="ds-l-row">
          <article
            id="content"
            className="ds-content ds-l-md-col--8 ds-l-lg-col--9"
          >
            <NpdMarkdown content={content} />
            <p className="ds-u-margin-top--7 ds-u-margin-bottom--2">
              <a className="ds-c-link" href="#content">
                {t("providers.backtotop")}
              </a>
            </p>
          </article>
        </div>
      </main>
    </>
  )
}
