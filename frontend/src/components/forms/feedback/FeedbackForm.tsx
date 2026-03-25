import {
  Alert,
  Button,
  ChoiceList,
  Dialog,
  TextField,
} from "@cmsgov/design-system"
import { useRef, useState } from "react"
import { useForm, Controller } from "react-hook-form"
import type { SubmitHandler } from "react-hook-form"
import { useTranslation } from "react-i18next"
import { Altcha } from "./Altcha"

const ISSUE_KEYS = [
  "incorrect_practice_locations",
  "incorrect_phone_numbers",
  "incorrect_taxonomy_or_speciality",
  "incorrect_organization_affiliation",
  "incorrect_endpoint",
  "missing_information",
  "other",
] as const

type PresenterData = {
  recordName?: string
  recordId?: string
  npi?: string | null
}

type ReportIssueFormData = {
  issues: string[]
  details: string
  email: string
}

type Props = {
  presenterData: PresenterData
  onExit: () => void
  isOpen: boolean
}

export const FeedbackForm = ({ presenterData, onExit, isOpen }: Props) => {
  const { t } = useTranslation()
  const [dialogStatus, setDialogStatus] = useState<"form" | "success">("form")
  const [submitError, setSubmitError] = useState<string | null>(null)
  const altchaRef = useRef<{ value: string | null; reset: () => void }>(null)

  const {
    register,
    handleSubmit,
    control,
    watch,
    formState: { errors },
  } = useForm<ReportIssueFormData>({
    defaultValues: {
      issues: [],
      details: "",
      email: "",
    },
  })

  const maxChars = 500
  const selectedIssues = watch("issues")
  const hasOther = selectedIssues.includes("other")
  const detailsLength = watch("details")?.length ?? 0
  const isSubmitDisabled =
    selectedIssues.length === 0 || (hasOther && detailsLength === 0)

  const issueChoices = ISSUE_KEYS.map((key) => ({
    label: t(`feedback.form.issues.${key}`),
    value: key,
  }))

  const errorMessages = [
    ...(Object.values(errors)
      .map((error) => error?.message)
      .filter(Boolean) as string[]),
    ...(submitError ? [submitError] : []),
  ]

  const onSubmit: SubmitHandler<ReportIssueFormData> = async (formData) => {
    try {
      setSubmitError(null)

      const altchaValue = altchaRef.current?.value

      if (!altchaValue) {
        setSubmitError(t("feedback.form.captchaRequired"))
        return
      }

      const response = await fetch("/api/feedback/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...presenterData,
          ...formData,
          altcha: altchaRef.current?.value,
        }),
      })

      if (!response.ok) {
        const data = await response.json()
        setSubmitError(data.error || t("feedback.form.submitError"))

        // reset CAPTCHA on failure so user must re verify
        altchaRef.current?.reset()
        return
      }

      setDialogStatus("success")
    } catch (e) {
      setSubmitError(t("feedback.form.submitError"))
      console.error(e)
    }
  }

  return (
    <Dialog
      onExit={onExit}
      isOpen={isOpen}
      heading={t("feedback.form.heading")}
      backdropClickExits={false}
    >
      {dialogStatus === "form" ? (
        <form onSubmit={handleSubmit(onSubmit)}>
          <p className="ds-u-margin-bottom--3 ds-u-margin-top--0">
            {t("feedback.form.description")}
          </p>

          {errorMessages.length > 0 && (
            <Alert heading={t("feedback.form.errorHeading")} variation="error">
              <ul className="ds-c-list ds-c-list--bare">
                {errorMessages.map((message, index) => (
                  <li key={index}>{message}</li>
                ))}
              </ul>
            </Alert>
          )}

          <p className="ds-u-margin-bottom--3">
            <strong>{t("feedback.form.providerName")}</strong> <br />
            {presenterData.recordName}
          </p>

          <Controller
            name="issues"
            control={control}
            rules={{
              validate: (v) =>
                v.length > 0 || t("feedback.form.issuesRequired"),
            }}
            render={({ field }) => (
              <ChoiceList
                type="checkbox"
                errorMessage={errors.issues?.message}
                hint={t("feedback.form.issuesHint")}
                label={
                  <>
                    {t("feedback.form.issuesLabel")}
                    <span className="ds-u-color--error" aria-hidden="true">
                      *
                    </span>
                  </>
                }
                name="issues"
                choices={issueChoices.map((choice) => ({
                  ...choice,
                  checked: field.value?.includes(choice.value),
                }))}
                onChange={(e) => {
                  const { value, checked } = e.target as HTMLInputElement
                  const current: string[] = field.value ?? []
                  const next = checked
                    ? [...current, value]
                    : current.filter((v) => v !== value)
                  field.onChange(next)
                }}
              />
            )}
          />

          <div>
            <TextField
              {...register("details", {
                validate: (value) => {
                  if (value.length > maxChars)
                    return t("feedback.form.detailsReduceCount")
                  if (hasOther && !value.trim())
                    return t("feedback.form.detailsOtherRequired")
                  return true
                },
              })}
              label={
                <>
                  {t("feedback.form.detailsLabel")}
                  {hasOther && (
                    <span className="ds-u-color--error" aria-hidden="true">
                      *
                    </span>
                  )}
                </>
              }
              hint={t("feedback.form.detailsHint")}
              multiline
              rows={4}
              maxLength={maxChars}
              errorMessage={errors.details?.message}
              className="ds-u-margin-top--3"
            />
            <p className="ds-u-margin-top--1 ds-u-color--gray ds-u-font-size--sm">
              {detailsLength}/500
            </p>
          </div>

          <TextField
            {...register("email", {
              pattern: {
                value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                message: t("feedback.form.emailInvalid"),
              },
            })}
            label={t("feedback.form.emailLabel")}
            errorMessage={errors.email?.message}
            className="ds-u-margin-top--3 ds-u-margin-bottom--3"
          />

          <Alert heading={t("feedback.form.privacyHeading")} hideIcon>
            <p className="ds-u-margin-bottom--3">
              {t("feedback.form.privacyBody")}
            </p>
          </Alert>

          <fieldset className="ds-u-margin-top--4">
            <Altcha ref={altchaRef} />
          </fieldset>

          <div className="ds-u-margin-top--4 ds-u-display--flex ds-u-justify-content--end">
            <Button variation="ghost" onClick={onExit} type="button">
              {t("feedback.form.cancel")}
            </Button>

            <Button
              variation="solid"
              type="submit"
              className="ds-u-margin-left--2"
              disabled={isSubmitDisabled}
            >
              {t("feedback.form.submit")}
            </Button>
          </div>
        </form>
      ) : (
        <Alert heading={t("feedback.form.successHeading")} variation="success">
          <p>{t("feedback.form.successBody")}</p>
          <Button
            variation="solid"
            onClick={onExit}
            className="ds-u-margin-top--3"
          >
            {t("feedback.form.close")}
          </Button>
        </Alert>
      )}
    </Dialog>
  )
}
