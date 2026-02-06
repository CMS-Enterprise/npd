export const PaginationCaption = ({
  pagination: { page, page_size, total, count },
}: {
  pagination: PaginationState
}) => {
  const start = (page - 1) * page_size + 1
  return (
    <span role="caption">
      Showing {start} - {start - 1 + total} of {count}
    </span>
  )
}
