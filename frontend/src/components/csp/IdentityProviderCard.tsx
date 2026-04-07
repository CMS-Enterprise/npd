import styles from "./IdentityProviderCard.module.css"

interface IdentityProviderCardProps {
  logo: string
  logoAlt: string
  name: string
  description: string
  onSelect: () => void
  testId?: string
}

export const IdentityProviderCard = ({
  logo,
  logoAlt,
  name,
  description,
  onSelect,
  testId,
}: IdentityProviderCardProps) => {
  return (
    <button
      type="button"
      className={styles.card}
      onClick={onSelect}
      data-testid={testId}
    >
      <div className={styles.logoContainer}>
        <img src={logo} alt={logoAlt} className={styles.logo} />
      </div>
      <div className={styles.content}>
        <span className={styles.name}>{name}</span>
        <span className={styles.description}>{description}</span>
      </div>
      <div className={styles.iconContainer}>
        <svg
          width="20"
          height="20"
          viewBox="0 0 20 20"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          <path
            d="M15 10.833V15.833C15 16.275 14.824 16.699 14.512 17.012C14.199 17.324 13.775 17.5 13.333 17.5H4.167C3.725 17.5 3.301 17.324 2.988 17.012C2.676 16.699 2.5 16.275 2.5 15.833V6.667C2.5 6.225 2.676 5.801 2.988 5.488C3.301 5.176 3.725 5 4.167 5H9.167"
            stroke="#71767a"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M12.5 2.5H17.5V7.5"
            stroke="#71767a"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M8.333 11.667L17.5 2.5"
            stroke="#71767a"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </div>
    </button>
  )
}
