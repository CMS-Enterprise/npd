import { screen, waitFor, within } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { render } from "../../../tests/render"
import { TaxonomySection } from "./TaxonomySection"

describe("Taxonomy Section", () => {
  it("does not render a table when an empty array is passed", async () => {
    render(<TaxonomySection taxonomyData={[]}/>)
    await waitFor(() => {
      expect(screen.queryByText("No taxonomy information available")).toBeInTheDocument();
      expect(screen.queryByRole("table")).not.toBeInTheDocument();
    })
  })
  it("renders a table of taxonomies when a single taxonomy is passed", async () => {
    const taxonomyData = [{
      nuccCode: "1234",
      display: "Surgery",
    },]
    render(<TaxonomySection taxonomyData={taxonomyData}/>)
    await waitFor(() => {
      expect(screen.queryByText("No taxonomy information available")).not.toBeInTheDocument();
      const table = screen.getByRole("table");
      expect(table).toBeInTheDocument();
      expect(
        within(table).getByText("NUCC Code", { selector: "th" }),
      ).toBeInTheDocument();
      expect(
        within(table).getByText("Description", { selector: "th" }),
      ).toBeInTheDocument();
      taxonomyData.forEach((taxonomy, index) => {
        const taxonomyRow = screen.getByTestId(`taxonomy-data-${index}`);
        expect(taxonomyRow).toBeInTheDocument();
        expect(
          within(taxonomyRow).getByText(taxonomy.nuccCode, { selector: "td" }),
        ).toBeInTheDocument();
        expect(
          within(taxonomyRow).getByText(taxonomy.display, { selector: "td" }),
        ).toBeInTheDocument();
    })
  })
})
  it("renders a table of taxonomies when multiple taxonomies are passed", async () => {
    const taxonomyData = [{
      nuccCode: "1234",
      display: "Surgery",
    },{
      nuccCode: "5555",
      display: "Oncology",
    },]
    render(<TaxonomySection taxonomyData={taxonomyData}/>)
    await waitFor(() => {
      expect(screen.queryByText("No taxonomy information available")).not.toBeInTheDocument();
      const table = screen.getByRole("table");
      expect(table).toBeInTheDocument();
      expect(
        within(table).getByText("NUCC Code", { selector: "th" }),
      ).toBeInTheDocument();
      expect(
        within(table).getByText("Description", { selector: "th" }),
      ).toBeInTheDocument();
      taxonomyData.forEach((taxonomy, index) => {
        const taxonomyRow = screen.getByTestId(`taxonomy-data-${index}`);
        expect(taxonomyRow).toBeInTheDocument();
        expect(
          within(taxonomyRow).getByText(taxonomy.nuccCode, { selector: "td" }),
        ).toBeInTheDocument();
        expect(
          within(taxonomyRow).getByText(taxonomy.display, { selector: "td" }),
        ).toBeInTheDocument();
    })
      
    })
  })
})
