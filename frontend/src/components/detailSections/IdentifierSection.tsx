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
    identifierData: Array<{
      type: string | undefined | null,
      number: string | undefined | null,
      details?: string
    }>,
    subsection?: boolean
}

export const IdentifierSection = ({identifierData, subsection=false}: Props) => {
    const { t } = useTranslation()
    const title = t("detailsections.identifiers.title")
    const fallback = t("detailsections.identifiers.fallback")
    return (
        <SectionWithContentOrFallback title={title} fallback={fallback} arrayData={identifierData} subsection={subsection}>
                    <Table data-testid="identifier-table">
                        <TableHead>
                          <TableRow>
                            <TableCell>
                              {t("detailsections.identifiers.type")}
                            </TableCell>
                            <TableCell>
                              {t("detailsections.identifiers.number")}
                            </TableCell>
                            <TableCell>
                              {t("detailsections.identifiers.details")}
                            </TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {identifierData.map((identifier, index) => (
                            <TableRow key={index} data-testid={`identifier-data-${index}`}>
                              <TableCell>{identifier.type}</TableCell>
                              <TableCell>{identifier.number}</TableCell>
                              <TableCell>{identifier.details}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                  </SectionWithContentOrFallback>
    )
}