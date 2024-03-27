import axios, { AxiosError, type AxiosResponse } from 'axios'

import {
        type ApiResponse,
        type ApiResponseWithPagination,
        type ErrorMessage,
        type DeleteResponse
    } from '@type/Api.types'
import { type LoginResponse } from '@type/Authorisation.types'
import type { OperatingCompanies, OperatingCompany } from '@/types/OperatingCompany.types'
import { type Account } from '@type/Account.types'
import { type Vehicle } from '@type/Vehicle.types'

// async function api(path: string, options: RequestInit | undefined = undefined) {
//     const response: Response = await fetch(`${import.meta.env.BACKEND_BASE}${path}`, options)

//     if (!response.ok) throw new Error();

//     return await response.json()
// }

const api = axios.create({ baseURL: import.meta.env.BACKEND_BASE })

export async function login(username: string, password: string): Promise<LoginResponse> {
    // const loginResponse: LoginResponse =
    //     await api("/api/v1/authorisation/token", { method: "POST", body: `username=${username}&password=${password}`, headers: { "Content-Type": "application/x-www-form-urlencoded" } })

    try {
        const loginResponse: AxiosResponse<LoginResponse> =
            await api.post("/api/v1/authorisation/token", `username=${username}&password=${password}`)

        return loginResponse.data
    } catch(e: any) {
        if(e?.response?.data?.message) throw Error(e.response.data.message, { cause: "safe" })

        throw Error("An unexpected error has occured!", { cause: "safe" })
    }
}

export async function refresh(accessToken: string, refreshToken: string): Promise<LoginResponse> {
    try {
        const loginResponse: AxiosResponse<LoginResponse> =
            await api.post("/api/v1/authorisation/refresh", `refresh_token=${refreshToken}`, { headers: { Authorization: `Bearer ${accessToken}`} })

        return loginResponse.data
    } catch(e: any) {
        if(e?.response?.data?.message) throw Error(e.response.data.message, { cause: "safe" })

        throw Error("An unexpected error has occured!", { cause: "safe" })
    }
}

export async function getOperatingCompanies(
    {
        limit,
        offset,
        orderBy: order_by,
        orderByDirection: order_by_direction
    }: {
            limit: string | number,
            offset: string | number,
            orderBy: string,
            orderByDirection: string
        },
        accessToken: string | null
    ): Promise<ApiResponseWithPagination<OperatingCompany>> {

    const queryParams: Record<string, string> = {
        limit: limit.toString(),
        offset: offset.toString(),
        order_by,
        order_by_direction
    }

    try {
        const reponse: AxiosResponse<ApiResponseWithPagination<OperatingCompany>> =
            await api.get("/api/v1/operating-company/", { params: queryParams, headers: { Authorization: `Bearer ${accessToken}`} })

        return reponse.data
    } catch(e: any) {
        if(e?.response?.data?.message) throw Error(e.response.data.message, { cause: "safe" })

        throw Error("An unexpected error has occured!", { cause: "safe" })
    }
}

export async function newOperatingCompany(
    {
        noc,
        shortCode,
        name
    }: {
            noc: string,
            shortCode: string,
            name: string
        },
        accessToken: string | null
    ): Promise<ApiResponse<OperatingCompany>> {

    const queryParams: Record<string, string> = {
            noc,
            short_code: shortCode,
            name,
        }

    try {
        const reponse: AxiosResponse<ApiResponse<OperatingCompany>> =
            await api.post("/api/v1/operating-company/", queryParams, { headers: { Authorization: `Bearer ${accessToken}`} })

        return reponse.data
    } catch(e: any) {
        if(e?.response?.data?.message) throw Error(e.response.data.message, { cause: "safe" })

        throw Error("An unexpected error has occured!", { cause: "safe" })
    }
}

export async function getOperatingCompany(
        id: string,
        accessToken: string | null
    ): Promise<ApiResponse<OperatingCompany>> {
    try {
        const reponse: AxiosResponse<ApiResponse<OperatingCompany>> =
            await api.get(`/api/v1/operating-company/${id}`, { headers: { Authorization: `Bearer ${accessToken}`} })

        return reponse.data
    } catch(e: any) {
        if(e?.response?.data?.message) throw Error(e.response.data.message, { cause: "safe" })

        throw Error("An unexpected error has occured!", { cause: "safe" })
    }
}

export async function editOperatingCompany(
    {
        id,
        noc,
        shortCode,
        name
    }: {
            id: string,
            noc: string,
            shortCode: string,
            name: string
        },
        accessToken: string | null
    ): Promise<ApiResponse<OperatingCompany>> {

    const queryParams: Record<string, string> = {
            noc,
            short_code: shortCode,
            name,
        }

    try {
        const reponse: AxiosResponse<ApiResponse<OperatingCompany>> =
            await api.put(`/api/v1/operating-company/${id}`, queryParams, { headers: { Authorization: `Bearer ${accessToken}`} })

        return reponse.data
    } catch(e: any) {
        if(e?.response?.data?.message) throw Error(e.response.data.message, { cause: "safe" })

        throw Error("An unexpected error has occured!", { cause: "safe" })
    }
}

export async function deleteOperatingCompany(
    {
        id,
        confirmed = false
    }: {
            id: string,
            confirmed: boolean
        },
        accessToken: string | null
    ): Promise<DeleteResponse> {

    const queryParams: Record<string, boolean> = {
            confirmed
        }

    try {
        const reponse: AxiosResponse<DeleteResponse> =
            await api.delete(`/api/v1/operating-company/${id}`, { params: queryParams, headers: { Authorization: `Bearer ${accessToken}`} })

        return reponse.data
    } catch(e: any) {
        if(e?.response?.data?.message) throw Error(e.response.data.message, { cause: "safe" })

        throw Error("An unexpected error has occured!", { cause: "safe" })
    }
}

export async function getAccounts(
    {
        limit,
        offset,
        orderBy: order_by,
        orderByDirection: order_by_direction
    }: {
            limit: string | number,
            offset: string | number,
            orderBy: string,
            orderByDirection: string
        },
        accessToken: string | null
    ): Promise<ApiResponseWithPagination<Account>> {

    const queryParams: Record<string, string> = {
        limit: limit.toString(),
        offset: offset.toString(),
        order_by,
        order_by_direction
    }

    try {
        const reponse: AxiosResponse<ApiResponseWithPagination<Account>> =
            await api.get("/api/v1/account/", { params: queryParams, headers: { Authorization: `Bearer ${accessToken}`} })

        return reponse.data
    } catch(e: any) {
        if(e?.response?.data?.message) throw Error(e.response.data.message, { cause: "safe" })

        throw Error("An unexpected error has occured!", { cause: "safe" })
    }
}

export async function getAccount(
    {
        id,
        // uuid,
        // username
    }: {
            id: string | undefined,
            // uuid: string | undefined,
            // username: string | undefined
        },
        accessToken: string | null
    ): Promise<ApiResponse<Account>> {

    try {
        const reponse: AxiosResponse<ApiResponse<Account>> =
            await api.get(`/api/v1/account/${id}`, { headers: { Authorization: `Bearer ${accessToken}`} })

        return reponse.data
    } catch(e: any) {
        if(e?.response?.data?.message) throw Error(e.response.data.message, { cause: "safe" })

        throw Error("An unexpected error has occured!", { cause: "safe" })
    }
}

export async function editAccount(
    {
        id,
        uuid,
        username,
        name,
        role,
        disabled,
    }: {
            id: string | undefined,
            uuid: string | undefined,
            username: string | undefined,
            name: string | undefined,
            role: string | undefined,
            disabled: boolean | undefined,
        },
        accessToken: string | null
    ): Promise<ApiResponse<Account>> {

    const queryParams: Record<string, string | boolean> = {
            ...id && { id },
            ...uuid && { uuid },
            ...username && { username },
            ...name && { name },
            ...role && { role },
            ...disabled && { disabled },
            ...{ last_modified: (new Date()).toISOString() },
        }

    try {
        const reponse: AxiosResponse<ApiResponse<Account>> =
            await api.put(`/api/v1/account/${id}`, queryParams, { headers: { Authorization: `Bearer ${accessToken}`} })

        return reponse.data
    } catch(e: any) {
        if(e?.response?.data?.message) throw Error(e.response.data.message, { cause: "safe" })

        throw Error("An unexpected error has occured!", { cause: "safe" })
    }
}

export async function newAccount(
    {
        username,
        name,
        role,
        disabled,
        password
    }: {
            username: string,
            name: string,
            role: string,
            disabled: boolean,
            password: string,
        },
        accessToken: string | null
    ): Promise<ApiResponse<Account>> {

    const queryParams: Record<string, string | boolean> = {
            username,
            name,
            role,
            disabled,
            password
        }

    try {
        const reponse: AxiosResponse<ApiResponse<Account>> =
            await api.post(`/api/v1/account/`, queryParams, { headers: { Authorization: `Bearer ${accessToken}`} })

        return reponse.data
    } catch(e: any) {
        if(e?.response?.data?.message) throw Error(e.response.data.message, { cause: "safe" })

        throw Error("An unexpected error has occured!", { cause: "safe" })
    }
}

export async function getVehicles(
    {
        limit,
        offset,
        orderBy: order_by,
        orderByDirection: order_by_direction
    }: {
            limit: string | number,
            offset: string | number,
            orderBy: string,
            orderByDirection: string
        },
        accessToken: string | null
    ): Promise<ApiResponseWithPagination<Vehicle>> {

    const queryParams: Record<string, string> = {
        limit: limit.toString(),
        offset: offset.toString(),
        order_by,
        order_by_direction
    }

    try {
        const reponse: AxiosResponse<ApiResponseWithPagination<Vehicle>> =
            await api.get("/api/v1/vehicle/", { params: queryParams, headers: { Authorization: `Bearer ${accessToken}`} })

        return reponse.data
    } catch(e: any) {
        if(e?.response?.data?.message) throw Error(e.response.data.message, { cause: "safe" })

        throw Error("An unexpected error has occured!", { cause: "safe" })
    }
}

export async function getVehicle(
    {
        fleet_no,
    }: {
            fleet_no: string | undefined,
        },
        accessToken: string | null
    ): Promise<ApiResponse<Vehicle>> {

    try {
        const reponse: AxiosResponse<ApiResponse<Vehicle>> =
            await api.get(`/api/v1/vehicle/${fleet_no}`, { headers: { Authorization: `Bearer ${accessToken}`} })

        return reponse.data
    } catch(e: any) {
        if(e?.response?.data?.message) throw Error(e.response.data.message, { cause: "safe" })

        throw Error("An unexpected error has occured!", { cause: "safe" })
    }
}

export async function newVehicle(
    {
        fleet_no,
        opco_id,
    }: {
            fleet_no: number,
            opco_id: number,
        },
        accessToken: string | null
    ): Promise<ApiResponse<Vehicle>> {
    const queryParams: Record<string, number> = {
            fleet_no,
            opco_id
        }

    try {
        const reponse: AxiosResponse<ApiResponse<Vehicle>> =
            await api.post(`/api/v1/vehicle/`, queryParams, { headers: { Authorization: `Bearer ${accessToken}`} })

        return reponse.data
    } catch(e: any) {
        if(e?.response?.data?.message) throw Error(e.response.data.message, { cause: "safe" })

        throw Error("An unexpected error has occured!", { cause: "safe" })
    }
}
