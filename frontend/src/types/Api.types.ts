export interface ApiResponse<T> {
    result: T,
}

export enum PaginationOrderDirection {
    ASCENDING = "ASC",
    DESCENDING = "DESC"
}

export interface Pagination {
    max: number
    limit: number
    offset: number
    orderBy: string
    orderByDirection: PaginationOrderDirection
}

export interface ApiResponseWithPagination<T> {
    result: T[],
    meta: Pagination
}

export interface ErrorMessage {
    message?: string
}

export interface DeleteResponse {
    message?: string
    result: {
        rows: any[][]
        length: number
    }
}
