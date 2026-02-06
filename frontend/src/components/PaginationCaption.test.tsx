import { render } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { PaginationCaption } from "./PaginationCaption"

describe("PaginationCaption", () => {
  it("shows correct pagination for first page", () => {
    const pagination: PaginationState = {
      page: 1,
      page_size: 10,
      total: 10,
      count: 26,
      totalPages: 3,
    }
    const screen = render(<PaginationCaption pagination={pagination} />)
    expect(screen.getByRole("caption")).toHaveTextContent(
      "Showing 1 - 10 of 26",
    )
  })

  it("shows correct pagination for middle page", () => {
    const pagination: PaginationState = {
      page: 2,
      page_size: 10,
      total: 10,
      count: 26,
      totalPages: 3,
    }
    const screen = render(<PaginationCaption pagination={pagination} />)
    expect(screen.getByRole("caption")).toHaveTextContent(
      "Showing 11 - 20 of 26",
    )
  })

  it("shows correct pagination for last page", () => {
    const pagination: PaginationState = {
      page: 3,
      page_size: 10,
      total: 6,
      count: 26,
      totalPages: 3,
    }
    const screen = render(<PaginationCaption pagination={pagination} />)
    expect(screen.getByRole("caption")).toHaveTextContent(
      "Showing 21 - 26 of 26",
    )
  })
})
