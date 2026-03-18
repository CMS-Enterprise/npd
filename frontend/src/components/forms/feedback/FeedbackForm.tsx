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
import { Altcha } from "./Altcha"

const ISSUE_CHOICES = [
  { label: "Practice location(s)", value: "incorrect_locations" },
  { label: "Phone number(s)", value: "incorrect_phone" },
  { label: "Taxonomy(-ies)/specialty(-ies)", value: "incorrect_taxonomy" },
  { label: "Organization affiliation (s)", value: "incorrect_org_affiliation" },
  { label: "FHIR endpoint", value: "incorrect_endpoint" },
  { label: "Missing information", value: "missing_information" },
  { label: "Other (specify below)", value: "other" },
]

type PresenterData = {
  recordName?: string
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
        setSubmitError("Please complete the CAPTCHA verification")
        return
      }

      const response = await fetch("/api/feedback/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          uuid: crypto.randomUUID(),
          ...presenterData,
          ...formData,
          altcha: altchaRef.current?.value,
        }),
      })

      if (!response.ok) {
        const data = await response.json()
        setSubmitError(data.error || "Something went wrong. Please try again.")

        // reset CAPTCHA on failure so user must re verify
        altchaRef.current?.reset()
        return
      }

      setDialogStatus("success")
    } catch (e) {
      setSubmitError(
        "There was an error in submitting the form. Please try again.",
      )
      console.error(e)
    }
  }

  return (
    <Dialog
      onExit={onExit}
      isOpen={isOpen}
      heading="Report an issue"
      backdropClickExits={false}
    >
      {dialogStatus === "form" ? (
        <form onSubmit={handleSubmit(onSubmit)}>
          <p className="ds-u-margin-bottom--3 ds-u-margin-top--0">
            Report inaccurate provider information to help us maintain the
            quality of the National Provider Directory. We may use this
            information to improve our data collection in the future.
          </p>

          {errorMessages.length > 0 && (
            <Alert
              heading="This form contains the following errors"
              variation="error"
            >
              <ul className="ds-c-list ds-c-list--bare">
                {errorMessages.map((message, index) => (
                  <li key={index}>{message}</li>
                ))}
              </ul>
            </Alert>
          )}

          <p className="ds-u-margin-bottom--3">
            <strong>Provider name</strong> <br />
            {presenterData.recordName}
          </p>

          <Controller
            name="issues"
            control={control}
            rules={{
              validate: (v) => v.length > 0 || "Select at least one issue",
            }}
            render={({ field }) => (
              <ChoiceList
                type="checkbox"
                errorMessage={errors.issues?.message}
                hint="Select all that apply"
                label={
                  <>
                    What issue(s) do you want to report on this profile?
                    <span className="ds-u-color--error" aria-hidden="true">
                      *
                    </span>
                  </>
                }
                name="issues"
                choices={ISSUE_CHOICES.map((choice) => ({
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
                  if (value.length > maxChars) return "Reduce character count"
                  if (hasOther && !value.trim())
                    return "Please provide details for 'Other"
                  return true
                },
              })}
              label={
                <>
                  Please provide details about the issue(s)
                  {hasOther && (
                    <span className="ds-u-color--error" aria-hidden="true">
                      *
                    </span>
                  )}
                </>
              }
              hint="Describe what information is incorrect or outdated and what corrections should be made, if known"
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
                message: "Enter a valid email address",
              },
            })}
            label="Email address"
            errorMessage={errors.email?.message}
            className="ds-u-margin-top--3 ds-u-margin-bottom--3"
          />

          <Alert heading="Privacy notice" hideIcon>
            <p className="ds-u-margin-bottom--3">
              The information you provide will be used solely to improve the
              accuracy of the National Provider Directory. Your email will only
              be used to send you updates about this specific issue submission.
            </p>
          </Alert>

          <fieldset className="ds-u-margin-top--4">
            <Altcha ref={altchaRef} />
          </fieldset>

          <div className="ds-u-margin-top--4 ds-u-display--flex ds-u-justify-content--end">
            <Button variation="ghost" onClick={onExit} type="button">
              Cancel
            </Button>

            <Button
              variation="solid"
              type="submit"
              className="ds-u-margin-left--2"
              disabled={isSubmitDisabled}
            >
              Submit
            </Button>
          </div>
        </form>
      ) : (
        <Alert heading="Issue reported" variation="success">
          <p>
            Thanks for helping improve the directory. Your report has been
            submitted and our team will review it.
          </p>
          <Button
            variation="solid"
            onClick={onExit}
            className="ds-u-margin-top--3"
          >
            Close
          </Button>
        </Alert>
      )}
    </Dialog>
  )
}
