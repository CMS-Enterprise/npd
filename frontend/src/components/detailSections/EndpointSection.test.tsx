import { screen, waitFor, within } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { render } from "../../../tests/render"
import { EndpointSection } from "./EndpointSection"

describe("Endpoint Section", () => {
  it("does not render a table when an empty array is passed", async () => {
    render(<EndpointSection endpointData={[]}/>)
    await waitFor(() => {
      expect(screen.queryByText("No endpoint information available")).toBeInTheDocument();
      expect(screen.queryByRole("table")).not.toBeInTheDocument();
    })
  })
  it("renders a table of endpoints when a single endpoint is passed", async () => {
    const endpointData = [{
      id: "123",
      address: 'test.org',
      connectionType: 'HL7 FHIR'
    }]
    render(<EndpointSection endpointData={endpointData}/>)
    await waitFor(() => {
      expect(screen.queryByText("No endpoint information available")).not.toBeInTheDocument();
      const table = screen.getByRole("table");
      expect(table).toBeInTheDocument();
      expect(
        within(table).getByText("Address", { selector: "th" }),
      ).toBeInTheDocument();
      expect(
        within(table).getByText("Connection Type", { selector: "th" }),
      ).toBeInTheDocument();
      endpointData.forEach(endpoint => {
        const endpointRow = screen.getByTestId(`endpoint-data-${endpoint.id}`);
        expect(endpointRow).toBeInTheDocument();
        expect(
          within(endpointRow).getByText(endpoint.connectionType, { selector: "td" }),
        ).toBeInTheDocument();
        expect(
          within(endpointRow).getByText(endpoint.address, { selector: "td" }),
        ).toBeInTheDocument();
    })
  })
})
  it("renders a table of endpoints when multiple endpoints are passed", async () => {
    const endpointData = [{
      id: "123",
      address: 'test.org',
      connectionType: 'HL7 FHIR'
    },
    {
        id: "1234",
        address: 'test@secure-mail.org',
        connectionType: 'DIRECT'
      }]
    render(<EndpointSection endpointData={endpointData}/>)
    await waitFor(() => {
      expect(screen.queryByText("No endpoint information available")).not.toBeInTheDocument();
      const table = screen.getByRole("table");
      expect(table).toBeInTheDocument();
      expect(
        within(table).getByText("Address", { selector: "th" }),
      ).toBeInTheDocument();
      expect(
        within(table).getByText("Connection Type", { selector: "th" }),
      ).toBeInTheDocument();
      endpointData.forEach(endpoint => {
        const endpointRow = screen.getByTestId(`endpoint-data-${endpoint.id}`);
        expect(endpointRow).toBeInTheDocument();
        expect(
          within(endpointRow).getByText(endpoint.connectionType, { selector: "td" }),
        ).toBeInTheDocument();
        expect(
          within(endpointRow).getByText(endpoint.address, { selector: "td" }),
        ).toBeInTheDocument();
      })
      
    })
  })
})
