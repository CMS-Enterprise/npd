import classNames from "classnames"
import React from "react"
import type { IconBaseProps } from "react-icons"

import layout from "../pages/Layout.module.css"

type Props = React.PropsWithChildren<{
  title?: string
  icon?: React.ReactElement<IconBaseProps>
  color?: string
  className?: string
}>

export const TitlePanel = ({
  title,
  icon,
  color,
  children,
  className,
}: Props) => {
  const bannerClass = classNames(layout.banner, className)

  const coloredIcon = icon && color ? React.cloneElement(icon, {color}) : icon

  return (
    <section className={bannerClass}>
      <div className="ds-l-container">
        <div className="ds-l-row">
          <div className="ds-l-col--12">
            <div className={layout.leader}>
              {coloredIcon && (
                <div className="ds-u-margin-bottom--1">{coloredIcon}</div>
              )}

              {title && (
                <div
                  role="heading"
                  aria-level={1}
                  className={layout.title}
                  style={{ color }}
                >
                  {title}
                </div>
              )}
            </div>
          </div>
        </div>

        {children}
      </div>
    </section>
  )
}
