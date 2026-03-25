import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableRow,
} from "@cmsgov/design-system"

import { SectionWithContentOrFallback } from "./SectionWithContentOrFallback"

import { useTranslation } from "react-i18next"
import type { ContactPoint } from "../../@types/fhir/ContactPoint"

type Props = {
    locationData: Array<{
      id: string | undefined,
      name: string | undefined | null,
      address: string,
      contact?: Array<ContactPoint> | null | undefined
    }>,
    subsection?: boolean
}

export const LocationSection = ({locationData, subsection = false}: Props) => {
    const { t } = useTranslation()
    const title = t("detailsections.locations.title")
    const fallback = t("detailsections.locations.fallback")
    return (
      <SectionWithContentOrFallback title={title} fallback={fallback} arrayData={locationData} subsection={subsection}>
        <Table data-testid="location-table">
            <TableHead>
              <TableRow>
                  <TableCell>{t("detailsections.locations.name")}</TableCell>
                  <TableCell>{t("detailsections.locations.address")}</TableCell>
                  <TableCell>{t("detailsections.locations.contact")}</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {locationData.map((location) => (
                  <TableRow key={location.id} data-testid={`location-data-${location.id}`}>
                    <TableCell>{location.name}</TableCell>
                    <TableCell>{location.address}</TableCell>
                {location.contact?.length !== undefined && location.contact?.length > 0 ? (
                    <TableCell>
                    <strong>{t("detailsections.locations.phone")}: </strong>
                    {location.contact.filter(contact => contact.system == 'phone')[0]?.value}
                    <br></br>
                    <strong>{t("detailsections.locations.fax")}: </strong>
                    {location.contact.filter(contact => contact.system == 'fax')[0]?.value}
                    </TableCell>) : 
                    (<TableCell>{t("detailsections.locations.noContact")}</TableCell>)}
                  </TableRow>
              ))}
            </TableBody>
          </Table>
      </SectionWithContentOrFallback>
    )
}