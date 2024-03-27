export enum RoleEnum {
    ADMIN = "ADM",
    STANDARD = "STD",
}

export interface Claims {
    sub: string
    name: string
    role: RoleEnum
    jti: string
    iat: number
    nbf: number
    exp: number
}
