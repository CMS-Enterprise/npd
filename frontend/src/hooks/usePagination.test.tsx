import { render } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import type { FHIRCollection, FHIROrganization } from "../@types/fhir"
import { usePagination } from "./usePagination"

type Props = {
  params: RequiredPaginationParams
  data?: FHIRCollection<unknown>
}

const TestComponent = ({ params, data }: Props) => {
  const pagination = usePagination(params, data)
  return (
    <>
      <span data-testid="page">{pagination.page}</span>
      <span data-testid="page_size">{pagination.page_size}</span>
      <span data-testid="total">{pagination.total}</span>
      <span data-testid="count">{pagination.count}</span>
      <span data-testid="totalPages">{pagination.totalPages}</span>
    </>
  )
}

describe("usePagination", () => {
  it("handles undefined data", () => {
    const screen = render(<TestComponent params={{ page: 1, page_size: 10 }} />)
    expect(screen.getByTestId("page")).toHaveTextContent("1")
    expect(screen.getByTestId("page_size")).toHaveTextContent("10")
    expect(screen.getByTestId("total")).toHaveTextContent("0")
    expect(screen.getByTestId("count")).toHaveTextContent("0")
    expect(screen.getByTestId("totalPages")).toHaveTextContent("1")
  })

  it("counts pages correctly", () => {
    const data: FHIRCollection<FHIROrganization> = {
      count: 26,
      next: "?page=2",
      previous: null,
      results: {
        resourceType: "Bundle",
        type: "searchset",
        total: 10,
        entry: [],
      },
    }
    const screen = render(
      <TestComponent params={{ page: 1, page_size: 10 }} data={data} />,
    )
    expect(screen.getByTestId("page")).toHaveTextContent("1")
    expect(screen.getByTestId("page_size")).toHaveTextContent("10")
    expect(screen.getByTestId("total")).toHaveTextContent("10")
    expect(screen.getByTestId("count")).toHaveTextContent("26")
    expect(screen.getByTestId("totalPages")).toHaveTextContent("3")
  })
})
