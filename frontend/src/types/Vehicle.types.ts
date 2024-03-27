import type { HypermediaLinks } from "./Hypermedia.types"

export interface Vehicle {
    fleet_no: number
    opco_id: number
    links?: HypermediaLinks
}

export type Vehicles = Vehicle[]
