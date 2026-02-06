type PaginationParams = {
  page?: number
  page_size?: number
}

type RequiredPaginationParams = Required<PaginationParams>

type PaginationState = RequiredPaginationParams & {
  total: number // number of records on current page
  count: number // total number of records in system
  totalPages: number
}
