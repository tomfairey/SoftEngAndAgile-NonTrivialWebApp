import type { HypermediaLinks } from "./Hypermedia.types"

export enum AccountRole {
    ADMIN = "ADM",
    STANDARD = "STD",
}

export interface Account {
    id: number
    uuid: string
    role: AccountRole
    username: string
    name: string
    password_last_modified: string
    disabled: boolean
    created_at: string
    last_modified: string
    links?: HypermediaLinks
}

export type Accounts = Account[]
