import type { HypermediaLinks } from "./Hypermedia.types"

export interface OperatingCompany {
    id: number
    noc: string
    short_code: string
    name: string
    links?: HypermediaLinks
}

export type OperatingCompanies = OperatingCompany[]
