import { type VerticalNavItemProps, VerticalNav } from "@cmsgov/design-system"
import classNames from "classnames"
import { useTranslation } from "react-i18next"

import { slugId } from "../../components/markdown/slug"

import layoutstyles from "../Layout.module.css"

export const AboutSidebarMenu = () => {
  const { t } = useTranslation()

  const sidebarClass = classNames(
    layoutstyles.sidebarNavContainer,
    "ds-u-margin-bottom--4",
    "ds-u-md-margin-bottom--0",
    "ds-l-md-col--4",
    "ds-l-lg-col--3",
  )

  const navItems: VerticalNavItemProps[] = [
    {
      id: "whatis-link",
      label: t("about.nav.whatis"),
      url: slugId(t("about.nav.whatis")),
    },
    {
      id: "howtosearch-link",
      label: t("about.nav.howtosearch"),
      url: slugId(t("about.nav.howtosearch")),
    },
    {
      label: t("about.nav.vision"),
      items: [
        {
          id: "visionpatients-link",
          label: t("about.nav.visionpatients"),
          url: slugId(t("about.nav.visionpatients")),
        },
        {
          id: "visionsystem-link",
          label: t("about.nav.visionsystem"),
          url: slugId(t("about.nav.visionsystem")),
        },
      ],
    },
    {
      id: "foundation-link",
      label: t("about.nav.foundation"),
      url: slugId(t("about.nav.foundation")),
    },
    {
      label: t("about.nav.accounts"),
      items: [
        {
          id: "alreadyhaveaccount-link",
          label: t("about.nav.alreadyhaveaccount"),
          url: slugId(t("about.nav.alreadyhaveaccount")),
        },
      ],
    },
    {
      id: "releasenotes-link",
      label: t("about.nav.releasenotes"),
      url: slugId(t("about.nav.releasenotes")),
    },
  ]

  return (
    <aside className={sidebarClass}>
      <VerticalNav className={layoutstyles.sidebarNav} items={navItems} />
    </aside>
  )
}
