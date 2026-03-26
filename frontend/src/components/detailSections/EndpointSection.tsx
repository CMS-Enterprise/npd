import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "@cmsgov/design-system"

import { useTranslation } from "react-i18next"
import { SectionWithContentOrFallback } from "./SectionWithContentOrFallback"

type Props = {
    endpointData: Array<{
      id: string | undefined,
      connectionType: string | undefined | null,
      address: string | undefined | null,
    } | undefined>,
    subsection?: boolean
}

export const EndpointSection = ({endpointData, subsection=false}: Props) => {
    const { t } = useTranslation()
        const title = t("detailsections.endpoints.title")
        const fallback = t("detailsections.endpoints.fallback")
        return (
          <SectionWithContentOrFallback title={title} fallback={fallback} arrayData={endpointData} subsection={subsection}>
            <Table data-testid='endpoint-table'>
              <TableHead>
                <TableRow>
                  <TableCell>
                    {t("detailsections.endpoints.connectionType")}
                  </TableCell>
                  <TableCell>{t("detailsections.endpoints.address")}</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
              {endpointData.map((endpoint) => (
                <TableRow key={endpoint?.id} data-testid={`endpoint-data-${endpoint?.id}`}>
                  <TableCell>{endpoint?.connectionType}</TableCell>
                  <TableCell>{endpoint?.address}</TableCell>
                </TableRow>
              ))}
              </TableBody>
            </Table>
          </SectionWithContentOrFallback>
        )
    }
    