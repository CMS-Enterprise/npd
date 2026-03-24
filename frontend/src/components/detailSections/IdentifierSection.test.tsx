import { screen, waitFor, within } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { render } from "../../../tests/render"
import { IdentifierSection } from "./IdentifierSection"

describe("Identifier Section", () => {
  it("does not render a table when an empty array is passed", async () => {
    render(<IdentifierSection identifierData={[]}/>)
    await waitFor(() => {
      expect(screen.queryByText("No identifiers available")).toBeInTheDocument();
      expect(screen.queryByRole("table")).not.toBeInTheDocument();
    })
  })
  it("renders a table of identifiers when a single identifier is passed", async () => {
    const identifierData = [{
      type: "NPI",
      number: '1234567890',
      details: 'issued 1/1/1900'
    }]
    render(<IdentifierSection identifierData={identifierData}/>)
    await waitFor(() => {
      expect(screen.queryByText("No identifiers available")).not.toBeInTheDocument();
      const table = screen.getByRole("table");
      expect(table).toBeInTheDocument();
      expect(
        within(table).getByText("Type", { selector: "th" }),
      ).toBeInTheDocument();
      expect(
        within(table).getByText("Number", { selector: "th" }),
      ).toBeInTheDocument();
      expect(
        within(table).getByText("Details", { selector: "th" }),
      ).toBeInTheDocument();
      identifierData.forEach((identifier, index) => {
        const identifierRow = screen.getByTestId(`identifier-data-${index}`);
        expect(identifierRow).toBeInTheDocument();
        expect(
          within(identifierRow).getByText(identifier.type, { selector: "td" }),
        ).toBeInTheDocument();
        expect(
          within(identifierRow).getByText(identifier.number, { selector: "td" }),
        ).toBeInTheDocument();
        expect(
          within(identifierRow).getByText(identifier.details, { selector: "td" }),
        ).toBeInTheDocument();
      })
    })
  })
  it("renders a table of identifiers when multiple identifiers are passed", async () => {
    const identifierData = [{
      type: "NPI",
      number: '1234567890',
      details: 'issued 1/1/1900'
    },
    {
      type: "MCR",
      number: '12345',
      details: ''
    }]
    render(<IdentifierSection identifierData={identifierData}/>)
    await waitFor(() => {
      expect(screen.queryByText("No identifiers available")).not.toBeInTheDocument();
      const table = screen.getByRole("table");
      expect(table).toBeInTheDocument();
      expect(
        within(table).getByText("Type", { selector: "th" }),
      ).toBeInTheDocument();
      expect(
        within(table).getByText("Number", { selector: "th" }),
      ).toBeInTheDocument();
      expect(
        within(table).getByText("Details", { selector: "th" }),
      ).toBeInTheDocument();
      identifierData.forEach((identifier, index) => {
        const identifierRow = screen.getByTestId(`identifier-data-${index}`);
        expect(identifierRow).toBeInTheDocument();
        expect(
          within(identifierRow).getByText(identifier.type, { selector: "td" }),
        ).toBeInTheDocument();
        expect(
          within(identifierRow).getByText(identifier.number, { selector: "td" }),
        ).toBeInTheDocument();
        expect(
          within(identifierRow).getByText(identifier.details, { selector: "td" }),
        ).toBeInTheDocument();
      })
    })
  })
})
