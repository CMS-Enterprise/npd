import { type VerticalNavItemProps, VerticalNav } from "@cmsgov/design-system"
import classNames from "classnames"
import { useTranslation } from "react-i18next"

import { slugId } from "../../components/markdown/slug"

import layoutstyles from "../Layout.module.css"

/*
 * Sidebar navigation is defined explicitly. When introducing a new heading tag
 * in markdown and a corresponding menu entry, _YOU ARE RESPONSIBLE_ for making
 * sure the translation text matches the link anchor id attribute associated
 * with the heading included in the markdown *.content.md file.
 *
 * The easiest way to do this is to make sure the translation text matches the
 * text used in .md and then using the slugId function for converting text into
 * an HTML-safe id attribute.
 *
 * For example, in developers.json, if we see:
 *
 *   { "nav": { "participating": "Participating in the test" } }
 *
 * Then we expect to see something like this in .content.md:
 *
 *   ### Participating in the test
 *
 * Which is converted to HTML:
 *
 *   <h3 id="participating-in-the-test"
 *
 * And in the menu component we see:
 *
 *   { url: slugId(t("developers.nav.participating")) }
 *
 * Is converted to:
 *
 *   <a href="#participating-in-the-test"
 *
 * Completing the relationship.
 */
export const SidebarMenu = () => {
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
      label: t("developers.nav.participating"),
      items: [
        {
          id: "participating-link",
          label: t("developers.nav.feedback"),
          url: slugId(t("developers.nav.feedback")),
        },
      ],
    },
    {
      id: "about-link",
      label: t("developers.nav.about"),
      url: slugId(t("developers.nav.about")),
    },
    {
      label: t("developers.nav.accessing"),
      items: [
        {
          id: "overview-link",
          label: t("developers.nav.overview"),
          url: slugId(t("developers.nav.overview")),
        },
        {
          id: "authentication-link",
          label: t("developers.nav.authentication"),
          url: slugId(t("developers.nav.authentication")),
        },
        {
          id: "endpoints-link",
          label: t("developers.nav.endpoints"),
          url: slugId(t("developers.nav.endpoints")),
        },
      ],
    },
    {
      id: "sandbox-link",
      label: t("developers.nav.sandbox"),
      url: slugId(t("developers.nav.sandbox")),
    },
    {
      id: "opensource-link",
      label: t("developers.nav.opensource"),
      url: slugId(t("developers.nav.opensource")),
    },
  ]

  return (
    <aside className={sidebarClass}>
      <VerticalNav className={layoutstyles.sidebarNav} items={navItems} />
    </aside>
  )
}
