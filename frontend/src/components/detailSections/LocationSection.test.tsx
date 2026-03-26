import { screen, waitFor, within } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { render } from "../../../tests/render"
import { LocationSection } from "./LocationSection"

describe("Location Section", () => {
  it("does not render a table when an empty array is passed", async () => {
    render(<LocationSection locationData={[]}/>)
    await waitFor(() => {
      expect(screen.queryByText("No location information available")).toBeInTheDocument();
      expect(screen.queryByRole("table")).not.toBeInTheDocument();
    })
  })
  it("renders a table of locations when a single location is passed", async () => {
    const locationData = [{
      id: "123",
      name: "Test Hospital",
      address: '123 Main Street, Anytown, USA',
      contact: [{'system': 'phone', 'value':'555-555-5555'}]
    },]
    render(<LocationSection locationData={locationData}/>)
    await waitFor(() => {
      expect(screen.queryByText("No location information available")).not.toBeInTheDocument();
      const table = screen.getByRole("table");
      expect(table).toBeInTheDocument();
      expect(
        within(table).getByText("Name", { selector: "th" }),
      ).toBeInTheDocument();
      expect(
        within(table).getByText("Address", { selector: "th" }),
      ).toBeInTheDocument();
      expect(
        within(table).getByText("Contact", { selector: "th" }),
      ).toBeInTheDocument();
      locationData.forEach(location => {
        const locationRow = screen.getByTestId(`location-data-${location.id}`);
        expect(locationRow).toBeInTheDocument();
        expect(
          within(locationRow).getByText(location.name, { selector: "td" }),
        ).toBeInTheDocument();
        expect(
          within(locationRow).getByText(location.address, { selector: "td" }),
        ).toBeInTheDocument();
        expect(
          within(locationRow).getByText(location.contact[0].value, { selector: "td" }),
        ).toBeInTheDocument();
    })
  })
})
  it("renders a table of locations when multiple locations are passed", async () => {
    const locationData = [{
      id: "123",
      name: "Test Hospital",
      address: '123 Main Street, Anytown, USA',
      contact: [{'system': 'phone', 'value':'555-555-5555'}]
    },
    {
      id: "1234",
      name: "Test Hospital 2",
      address: '123 Health Way, Anytown, USA',
      contact: [{'system': 'fax', 'value':'555-555-5555'}]
    }]
    render(<LocationSection locationData={locationData}/>)
    await waitFor(() => {
      expect(screen.queryByText("No location information available")).not.toBeInTheDocument();
      const table = screen.getByRole("table");
      expect(table).toBeInTheDocument();
      expect(
        within(table).getByText("Name", { selector: "th" }),
      ).toBeInTheDocument();
      expect(
        within(table).getByText("Address", { selector: "th" }),
      ).toBeInTheDocument();
      expect(
        within(table).getByText("Contact", { selector: "th" }),
      ).toBeInTheDocument();
      locationData.forEach(location => {
        const locationRow = screen.getByTestId(`location-data-${location.id}`);
        expect(locationRow).toBeInTheDocument();
        expect(
          within(locationRow).getByText(location.name, { selector: "td" }),
        ).toBeInTheDocument();
        expect(
          within(locationRow).getByText(location.address, { selector: "td" }),
        ).toBeInTheDocument();
        expect(
          within(locationRow).getByText(location.contact[0].value, { selector: "td" }),
        ).toBeInTheDocument();
      })
      
    })
  })
})
