import { screen, waitFor } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { render } from "../../../tests/render"
import { SectionWithContentOrFallback } from "./SectionWithContentOrFallback"

describe("Taxonomy Section", () => {
  it("does not render children an empty array is passed", async () => {
    render(<SectionWithContentOrFallback title="My cool Section" fallback="No arrayData available" arrayData={[]}>Hello World!</SectionWithContentOrFallback>)
    await waitFor(() => {
      expect(screen.queryByText("No arrayData available")).toBeInTheDocument();
      expect(screen.queryByText("Hello World!")).not.toBeInTheDocument();
    })
  })
  it("renders a child when a non-empty array is passed", async () => {
    render(<SectionWithContentOrFallback title="My cool Section" fallback="No arrayData available" arrayData={[1]}>Hello World!</SectionWithContentOrFallback>)
    await waitFor(() => {
      expect(screen.queryByText("No arrayData available")).not.toBeInTheDocument();
      expect(screen.queryByText("Hello World!")).toBeInTheDocument();
    })
  })
})
