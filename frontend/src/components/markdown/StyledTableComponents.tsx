import React from "react"

export const StyledTable = (props: React.ComponentPropsWithoutRef<"table">) =>
  React.createElement("table", { className: "ds-c-table", ...props })

export const StyledTh = (props: React.ComponentPropsWithoutRef<"th">) =>
  React.createElement("th", { className: "ds-c-table__header", ...props })

export const StyledTd = (props: React.ComponentPropsWithoutRef<"td">) =>
  React.createElement("td", { className: "ds-c-table__cell", ...props })
