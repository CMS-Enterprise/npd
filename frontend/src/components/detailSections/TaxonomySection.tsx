import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "@cmsgov/design-system"

import { SectionWithContentOrFallback } from "./SectionWithContentOrFallback"

import { useTranslation } from "react-i18next"

type Props = {
    taxonomyData: Array<{
      nuccCode: string | undefined | null,
      display: string | undefined | null,
    }>,
    subsection?: boolean
}

export const TaxonomySection = ({taxonomyData, subsection = false}: Props) => {
    const { t } = useTranslation()
    const title = t("detailsections.taxonomy.title")
    const fallback = t("detailsections.taxonomy.fallback")
    return (
        <SectionWithContentOrFallback title={title} fallback={fallback} arrayData={taxonomyData} subsection={subsection}>
                    <Table data-testid="taxonomy-table">
                        <TableHead>
                          <TableRow>
                            <TableCell>
                              {t("detailsections.taxonomy.nuccCode")}
                            </TableCell>
                            <TableCell>
                              {t("detailsections.taxonomy.taxonomy")}
                            </TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {taxonomyData.map((taxonomy, index) => (
                            <TableRow key={index} data-testid={`taxonomy-data-${index}`}>
                              <TableCell>{taxonomy.nuccCode}</TableCell>
                              <TableCell>{taxonomy.display}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                  </SectionWithContentOrFallback>
    )
}