import { SkipNav } from "@cmsgov/design-system"
import { useTranslation } from "react-i18next"

import classNames from "classnames"

import { NpdMarkdown } from "../../components/markdown/NpdMarkdown"
import { AboutHeading } from "./AboutHeading"
import { AboutSidebarMenu } from "./AboutSidebarMenu"
import { AuthCards } from "./AuthCards"

import layoutstyles from "../Layout.module.css"

import content from "./About.content.md?raw"

const SPLIT_MARKER = "<!-- AUTH_CARDS -->"

export const About = () => {
  const { t } = useTranslation()
  const contentClass = classNames(layoutstyles.content, "ds-l-container")

  const [beforeCards, afterCards] = content.split(SPLIT_MARKER)

  return (
    <>
      <AboutHeading />
      <main className={contentClass}>
        <SkipNav href="#content" />
        <div className="ds-l-row">
          <AboutSidebarMenu />
          <article
            id="content"
            className="ds-content ds-l-md-col--8 ds-l-lg-col--9"
          >
            <NpdMarkdown content={beforeCards} />
            <AuthCards />
            <NpdMarkdown content={afterCards} />
            <p className="ds-u-margin-top--7 ds-u-margin-bottom--2">
              <a className="ds-c-link" href="#content">
                {t("about.backtotop")}
              </a>
            </p>
          </article>
        </div>
      </main>
    </>
  )
}
