import layout from "../../Pages/Layout.module.css"

export const SectionWithContentOrFallback = ({title, arrayData, fallback, children, subsection = false, }: React.PropsWithChildren<{ title: string, arrayData: Array<unknown>, fallback: string, subsection?: boolean }>) => {
    if (arrayData.length > 0) {
        return (
          <section className={layout.section}>
            { !subsection ? (<h2>{title}</h2>) : (<h4>{title}</h4>)}
            {children}
            </section>
        )
    }
    else {
        return (
                <section className={layout.section}>
                  { !subsection ? (<h2>{title}</h2>) : (<h4>{title}</h4>)}
                  <p className="ds-u-color--gray">
                    {fallback}
                  </p>
                </section>
            )
    }
}