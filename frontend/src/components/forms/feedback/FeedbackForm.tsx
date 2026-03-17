import {
  Alert,
  Button,
  ChoiceList,
  Dialog,
  TextField,
} from "@cmsgov/design-system"
import { useState } from "react"
import { useForm, Controller } from "react-hook-form"
import type { SubmitHandler } from "react-hook-form"

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

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<ReportIssueFormData>({
    defaultValues: {
      issues: [],
      details: "",
      email: "",
    },
  })

  const onSubmit: SubmitHandler<ReportIssueFormData> = (formData) => {
    const uuid = crypto.randomUUID()

    const payload = {
      uuid,
      ...presenterData,
      ...formData,
    }

    // hook this up to django email
    console.log(payload)
    setDialogStatus("success")
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

          {/* <Alert
                        heading="This form contains the following errors"
                        variation="error"
                    >
                        {errors.details?.message}
                    </Alert> */}

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
                      {" "}
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

          <TextField
            {...register("details")}
            label="Please provide details about the issue(s)"
            hint="Describe what information is incorrect or outdated and what corrections should be made, if known"
            multiline
            rows={4}
            errorMessage={errors.details?.message}
            className="ds-u-margin-top--3"
          />

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

          <div className="ds-u-margin-top--4 ds-u-display--flex ds-u-justify-content--end">
            <Button variation="ghost" onClick={onExit} type="button">
              Cancel
            </Button>

            <Button
              variation="solid"
              type="submit"
              className="ds-u-margin-left--2"
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
