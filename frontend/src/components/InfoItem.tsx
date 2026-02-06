interface InfoItemProps {
    label: string
    value: string | null | undefined
  }
  
  // Reusable component for label/value pairs
  export const InfoItem = ({ label, value }: InfoItemProps) => (
    <div>
      <div className="ds-u-font-weight--bold ds-u-font-size--sm">{label}</div>
      <div className="ds-u-color--base">
        {value || <span className="ds-u-color--gray">—</span>}
      </div>
    </div>
  )