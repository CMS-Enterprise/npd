import { screen, waitFor } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { render } from "../../tests/render"
import { FeatureFlag } from "./FeatureFlag"

describe("FeatureFlag", () => {
  it("does not render content when feature flag is not set", async () => {
    render(<FeatureFlag name="SOMETHING">Some content</FeatureFlag>)
    await waitFor(() => {
      expect(screen.queryByText("Some content")).toBeNull()
    })
  })

  describe("inverse", () => {
    it("renders content when feature flag is not set and inverse is used", async () => {
      render(
        <FeatureFlag name="SOMETHING" inverse>
          Some content
        </FeatureFlag>,
      )
      await waitFor(() => {
        expect(screen.queryByText("Some content")).toBeInTheDocument()
      })
    })
  })

  describe("with SOMETHING set", () => {
    it("renders content", async () => {
      render(<FeatureFlag name="SOMETHING">Some content</FeatureFlag>, {
        settings: { feature_flags: { SOMETHING: true } },
      })
      await waitFor(() => {
        expect(screen.queryByText("Some content")).toBeInTheDocument()
      })
    })

    it("does not render inverse content", async () => {
      render(
        <FeatureFlag inverse name="SOMETHING">
          Some content
        </FeatureFlag>,
        { settings: { feature_flags: { SOMETHING: true } } },
      )
      await waitFor(() => {
        expect(screen.queryByText("Some content")).toBeNull()
      })
    })
  })
})
