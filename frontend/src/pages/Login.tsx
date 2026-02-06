import classNames from "classnames"

import { Alert } from "@cmsgov/design-system"
import { useTranslation } from "react-i18next"
import { CsrfInput } from "../components/forms/CsrfInput"
import { useDjangoForm } from "../hooks/useDjangoForm"
import { apiUrl } from "../state/api"

import styles from "./Login.module.css"

export const Login = () => {
  const { t } = useTranslation()
  const form = useDjangoForm()

  const nextUrl = form.next
  const mainClasses = classNames(styles.main)

  return (
    <main className={mainClasses}>
      <div className="ds-base ds-l-container">
        <div className="ds-l-row">
          <div className="ds-l-lg-col--6 ds-l-md-col--8">
            <div className={styles.spacer}></div>
            <div className={styles.card}>
              <form
                method="post"
                action={apiUrl("/accounts/login/")}
                className="usa-form"
                id="login-form"
              >
                <CsrfInput />
                <fieldset className="usa-fieldset">
                  <legend className="usa-legend usa-legend--large">
                    Sign in
                  </legend>
                  <p className={styles.description}>
                    The National Provider Directory is under development with
                    limited access for test users.
                  </p>
                  <label className="usa-label" htmlFor="username">
                    Username
                  </label>
                  <input
                    className="usa-input"
                    id="username"
                    name="username"
                    type="text"
                    autoCapitalize="off"
                    autoCorrect="off"
                    autoComplete="username"
                    autoFocus
                    required
                  />
                  <label className="usa-label" htmlFor="password">
                    Password
                  </label>
                  <input
                    className="usa-input"
                    id="password"
                    name="password"
                    type="password"
                    required
                  />
                  <button
                    title="Toggle password"
                    type="button"
                    className="usa-show-password"
                    aria-controls="password"
                    data-show-text="Show password"
                    data-hide-text="Hide password"
                  >
                    Show password
                  </button>
                  <input className="usa-button" type="submit" value="Sign in" />
                  {nextUrl && (
                    <input type="hidden" name="next" value={nextUrl} />
                  )}
                </fieldset>
              </form>
            </div>
            {form.errors && (
              <>
                <div className={styles.spacer}></div>
                <Alert
                  variation="error"
                  heading={t("landing.authentication.error.heading")}
                >
                  {form.errors["__all__"] &&
                    form.errors["__all__"].map((message) => (
                      <p key={message}>{message}</p>
                    ))}
                  <p>{t("landing.authentication.error.description")}</p>
                </Alert>
              </>
            )}
            <div className={styles.spacer}></div>
          </div>
        </div>
      </div>
    </main>
  )
}
