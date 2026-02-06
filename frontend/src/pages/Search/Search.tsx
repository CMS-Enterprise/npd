import { Button } from "@cmsgov/design-system"
import { FaUserMd, FaHospital } from "react-icons/fa"
import { TitlePanel } from "../../components/TitlePanel"
import layout from "../Layout.module.css"
import { useTranslation } from "react-i18next"

export const Search = () => {
  const { t } = useTranslation()

  return (
    <>
      <TitlePanel
        title={t("search.title")}
        className={layout.compactLeader}
      >
        <p>
        {t("search.subtitle")}
        </p>

        <div className="ds-l-row">
          <div className="ds-l-col--12 ds-u-display--flex ds-u-justify-content--start ds-u-margin-top--4 ds-u-margin-bottom--4">
            <Button
              variation="solid"
              size="big"
              href="/practitioners/search"
              className="ds-u-margin-right--2"
            >
              <FaUserMd className="ds-u-margin-right--1" aria-hidden="true" />
              {t("search.practitioner")}
            </Button>
            <Button
              variation="solid"
              size="big"
              href="/organizations/search"
            >
              <FaHospital className="ds-u-margin-right--1" aria-hidden="true" />
              {t("search.organization")}
            </Button>
          </div>
        </div>
      </TitlePanel>
    </>
  )
}