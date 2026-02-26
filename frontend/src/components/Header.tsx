import { Badge, Button, SkipNav, UsaBanner } from "@cmsgov/design-system"
import classnames from "classnames"
import { useTranslation } from "react-i18next"

import close from "@uswds/uswds/img/usa-icons/close.svg"
import cmsLogo from "../assets/cms-gov-logo.svg"
import { useFrontendSettings } from "../hooks/useFrontendSettings"
import { apiUrl } from "../state/api"
import { CsrfInput } from "./forms/CsrfInput"
import { getCookie } from "./getCookie"
import { slugId } from "./markdown/slug"

import styles from "./Header.module.css"

const AuthenticationControl = () => {
  const { t } = useTranslation()
  const {
    settings: { user },
    loading,
  } = useFrontendSettings()

  if (loading) {
    return null
  }

  const path = user?.is_anonymous ? "/accounts/login/" : "/accounts/logout/"
  const label = user?.is_anonymous
    ? t("header.auth.login")
    : t("header.auth.logout")

  if (user?.is_anonymous) {
    return (
      <li className="usa-nav__primary-item">
        <a href={path} className="ds-u-link">
          {label}
        </a>
      </li>
    )
  }
  return (
    <li className="usa-nav__primary-item">
      <form action={apiUrl(path)} id="authentication-form" method="POST">
        <CsrfInput />
        <input
          type="hidden"
          value={getCookie("csrftoken") || ""}
          name="csrfmiddlewaretoken"
        />
        <Button role="button" type="submit" variation="ghost">
          {label}
        </Button>
      </form>
    </li>
  )
}

type HeaderProps = {
  hideLinks?: boolean
}

export const Header = ({ hideLinks }: HeaderProps) => {
  const { t } = useTranslation()
  const {
    settings: { user },
  } = useFrontendSettings()
  const classes = classnames("usa-header", "usa-header--basic", styles.header)
  const badgeClasses = classnames(styles.betaBadge)
  const textContainerClasses = classnames(
    "ds-u-md-display--flex",
    "ds-u-display--none",
    styles.textContainer,
  )

  return (
    <>
      <SkipNav href="#after-header">{t("header.skip")}</SkipNav>
      <UsaBanner />
      <header className={classes} role="banner">
        <div className="usa-nav-container">
          <div className="usa-navbar">
            <div className={`usa-logo ${styles.title}`}>
              <a
                href="/"
                className="ds-u-display--flex ds-u-flex-direction--row ds-u-padding-left--0"
                title="Return to the homepage"
              >
                <img src={cmsLogo} className={styles.logo} alt="CMS.gov" />
                <div className={textContainerClasses}>
                  <em className={`${styles.logoText} usa-logo__text`}>
                    {t("header.title")}
                  </em>
                  <Badge variation="info" className={badgeClasses}>
                    {t("header.badge")}
                  </Badge>
                </div>
              </a>
            </div>
            {!hideLinks && (
              <button type="button" className="usa-menu-btn">
                Menu
              </button>
            )}
          </div>

          {!hideLinks && (
            <nav aria-label="Primary navigation" className="usa-nav">
              <button type="button" className="usa-nav__close">
                <img src={close} role="img" alt="Close" />
              </button>

              <ul className="usa-nav__primary usa-accordion" role="navigation">
                {user && !user?.is_anonymous && (
                  <>
                    <li className="usa-nav__primary-item">
                      <a href="/search" className="usa-nav__link">
                        <span>{t("header.link.search")}</span>
                      </a>
                    </li>
                    <li className="usa-nav__primary-item">
                      <button
                        type="button"
                        className="usa-accordion__button usa-nav__link"
                        aria-expanded="false"
                        aria-controls="basic-nav-section"
                      >
                        <span>{t("header.link.developers")}</span>
                      </button>
                      <ul
                        id="basic-nav-section"
                        className={`usa-nav__submenu ${styles.submenuList}`}
                        role="menu"
                        hidden
                      >
                        <li className="usa-nav__submenu-item">
                          <a
                            href={`/developers${slugId(t("developers.nav.participating"))}`}
                          >
                            <span>{t("developers.nav.participating")}</span>
                          </a>
                        </li>
                        <li className="usa-nav__submenu-item">
                          <a
                            href={`/developers${slugId(t("developers.nav.about"))}`}
                          >
                            <span>{t("developers.nav.about")}</span>
                          </a>
                        </li>
                        <li className="usa-nav__submenu-item">
                          <a
                            href={`/developers${slugId(t("developers.nav.accessing"))}`}
                          >
                            <span>{t("developers.nav.accessing")}</span>
                          </a>
                        </li>
                        <li className="usa-nav__submenu-item">
                          <a
                            href={`/developers${slugId(t("developers.nav.opensource"))}`}
                          >
                            <span>{t("developers.nav.opensource")}</span>
                          </a>
                        </li>
                      </ul>
                    </li>
                  </>
                )}

                <AuthenticationControl />
              </ul>
            </nav>
          )}
        </div>
      </header>
      <a id="after-header" />
    </>
  )
}
