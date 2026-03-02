import styles from "./DetailPageBanner.module.css"

interface DetailPageBannerProps {
  title: string
  subtitle?: string
  pageType: string
  backLink?: {
    label: string
    href: string
  }
}

export const DetailPageBanner = ({
  title,
  subtitle,
  pageType,
  backLink,
}: DetailPageBannerProps) => (
  <section className={styles.banner}>
    <div className="ds-l-container">
      <div className="ds-l-row">
        <div className="ds-l-col--12">
          {backLink && (
            <a href={backLink.href} className={styles.backLink}>
              {backLink.label}
            </a>
          )}
          <div className={styles.leader}>
            <span className={styles.resourceType}>{pageType}</span>
            <h1
              role="heading"
              data-testid="detail-banner-title"
              aria-level={1}
              className={styles.title}
            >
              {title}
            </h1>
            {subtitle && (
              <span
                data-testid="detail-banner-subtitle"
                className={styles.subtitle}
              >
                {subtitle}
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  </section>
)
